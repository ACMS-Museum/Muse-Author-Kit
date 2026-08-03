"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");

const vscode = require("vscode");

const DIAGNOSTIC_SOURCE = "muselang";

function resolveModulePath() {
  const workspaceFolders = vscode.workspace.workspaceFolders || [];
  for (const folder of workspaceFolders) {
    const candidate = path.join(folder.uri.fsPath, "muse-dev", "MuseLang", "V1", "src");
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }
  const bundled = path.resolve(__dirname, "..", "V1", "src");
  if (fs.existsSync(bundled)) {
    return bundled;
  }
  return undefined;
}

function makeTempSource(document) {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "muselang-"));
  const ext = path.extname(document.uri.fsPath || ".muse") || ".muse";
  const filePath = path.join(tempDir, `lint${ext}`);
  fs.writeFileSync(filePath, document.getText(), "utf8");
  return { tempDir, filePath };
}

function diagnosticFromResult(item, document) {
  const severity = item.severity === "warning" ? vscode.DiagnosticSeverity.Warning : vscode.DiagnosticSeverity.Error;
  const lineIndex = typeof item.line === "number" ? Math.max(0, item.line - 1) : 0;
  const line = document.lineAt(Math.min(lineIndex, Math.max(0, document.lineCount - 1)));
  const range = new vscode.Range(lineIndex < document.lineCount ? line.range.start : new vscode.Position(0, 0), line.range.end);
  const diagnostic = new vscode.Diagnostic(range, item.message, severity);
  diagnostic.source = DIAGNOSTIC_SOURCE;
  return diagnostic;
}

function genericDiagnostic(message, document) {
  const line = document.lineAt(0);
  const diagnostic = new vscode.Diagnostic(line.range, message, vscode.DiagnosticSeverity.Error);
  diagnostic.source = DIAGNOSTIC_SOURCE;
  return diagnostic;
}

function runLint(document) {
  const python = vscode.workspace.getConfiguration("muselang").get("pythonPath") || "python";
  const modulePath = resolveModulePath();
  if (!modulePath) {
    return {
      diagnostics: [genericDiagnostic("Could not locate the MuseLang Python package.", document)],
    };
  }

  const { tempDir, filePath } = makeTempSource(document);
  const env = { ...process.env };
  env.PYTHONPATH = env.PYTHONPATH ? `${modulePath}${path.delimiter}${env.PYTHONPATH}` : modulePath;

  try {
    const result = spawnSync(python, ["-m", "muselang.cli", "lint", filePath], {
      encoding: "utf8",
      env,
    });

    if (result.error) {
      return {
        diagnostics: [genericDiagnostic(`MuseLang linter could not start: ${result.error.message}`, document)],
      };
    }

    const stdout = (result.stdout || "").trim();
    if (!stdout) {
      const stderr = (result.stderr || "").trim();
      return {
        diagnostics: [genericDiagnostic(stderr || "MuseLang linter returned no output.", document)],
      };
    }

    let payload;
    try {
      payload = JSON.parse(stdout);
    } catch (error) {
      return {
        diagnostics: [genericDiagnostic(`MuseLang linter returned invalid JSON: ${error.message}`, document)],
      };
    }

    const diagnostics = [];
    for (const item of payload.diagnostics || []) {
      diagnostics.push(diagnosticFromResult(item, document));
    }
    if ((payload.status || "ok") !== "ok" && diagnostics.length === 0) {
      diagnostics.push(genericDiagnostic("MuseLang lint failed.", document));
    }
    return { diagnostics };
  } finally {
    try {
      fs.rmSync(tempDir, { recursive: true, force: true });
    } catch (_error) {
      // Ignore temp cleanup failures.
    }
  }
}

function activate(context) {
  const collection = vscode.languages.createDiagnosticCollection("muselang");
  context.subscriptions.push(collection);

  const pending = new Map();

  const refresh = (document) => {
    if (document.languageId !== "muselang") {
      return;
    }
    const existing = pending.get(document.uri.toString());
    if (existing) {
      clearTimeout(existing);
    }
    const timer = setTimeout(() => {
      const { diagnostics } = runLint(document);
      collection.set(document.uri, diagnostics);
      pending.delete(document.uri.toString());
    }, 250);
    pending.set(document.uri.toString(), timer);
  };

  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(refresh),
    vscode.workspace.onDidChangeTextDocument((event) => refresh(event.document)),
    vscode.workspace.onDidSaveTextDocument((document) => {
      if (vscode.workspace.getConfiguration("muselang").get("lintOnSave")) {
        refresh(document);
      }
    }),
    vscode.commands.registerCommand("muselang.lintCurrentDocument", () => {
      const editor = vscode.window.activeTextEditor;
      if (editor) {
        const { diagnostics } = runLint(editor.document);
        collection.set(editor.document.uri, diagnostics);
      }
    }),
  );

  for (const document of vscode.workspace.textDocuments) {
    refresh(document);
  }
}

function deactivate() {}

module.exports = {
  activate,
  deactivate,
};
