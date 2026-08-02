;;; muselang-mode.el --- Major mode for MuseLang V1 -*- lexical-binding: t; -*-
;;
;; Major mode for editing MuseLang V1 source files.
;;
;; Features:
;;
;;   * syntax highlighting for declarations, properties, actions, conditions,
;;     strings, comments, booleans, numbers and operators
;;   * automatic selection for .muse and .muselang files
;;   * indentation in two space steps
;;   * comment commands using #
;;   * automatic pairing of quotes and brackets through electric-pair-mode
;;   * Imenu navigation for top level declarations and nested blocks
;;   * skeleton insertion commands comparable to the VS Code snippets
;;   * optional Flymake diagnostics using the MuseLang command line linter
;;
;; Installation:
;;
;;   Copy this file somewhere on `load-path', then add this to init.el:
;;
;;     (require 'muselang-mode)
;;
;; The file associations are installed automatically.
;;
;; Flymake linting is enabled by default when both Flymake and the `muselang'
;; executable are available.  Set `muselang-enable-flymake' to nil before
;; loading the mode to disable it.  Set `muselang-linter-command' if the
;; executable has another name or requires an absolute path.

;;; Code:

(require 'cl-lib)
(require 'json)
(require 'skeleton)
(require 'subr-x)

(defgroup muselang nil
  "Editing MuseLang source files."
  :group 'languages)

(defcustom muselang-indent-offset 2
  "Number of spaces used for each MuseLang indentation level."
  :type 'integer
  :safe #'integerp
  :group 'muselang)

(defcustom muselang-enable-flymake t
  "Whether to enable MuseLang Flymake diagnostics when available."
  :type 'boolean
  :group 'muselang)

(defcustom muselang-linter-command "muselang"
  "MuseLang command used for lint diagnostics."
  :type 'string
  :group 'muselang)

(defconst muselang-declaration-keywords
  '("room" "type" "object" "obj" "character" "char" "rule" "verb"
    "dialogue" "node" "goal" "time" "exit")
  "Keywords that introduce MuseLang declarations or blocks.")

(defconst muselang-property-keywords
  '("alias" "desc" "description" "tag" "state" "portable" "visible"
    "from" "in" "on" "of" "to" "via")
  "MuseLang property and relationship keywords.")

(defconst muselang-control-keywords
  '("if" "elif" "else" "while" "until" "before" "after" "say" "hint"
    "set" "move" "place" "give" "show" "hide" "goto" "call" "end"
    "option")
  "MuseLang control and action keywords.")

(defconst muselang-word-operators '("not" "and" "or" "is")
  "MuseLang word operators.")

(defconst muselang-boolean-literals '("true" "false")
  "MuseLang boolean literals.")

(defconst muselang--identifier-regexp "[A-Za-z_][A-Za-z0-9_]*")

(defconst muselang-font-lock-keywords
  `((,(concat "^[[:space:]]*\\("
              (regexp-opt muselang-declaration-keywords t)
              "\\)\\_>[[:space:]]+\\("
              muselang--identifier-regexp
              "\\)")
     (1 font-lock-keyword-face)
     (2 font-lock-function-name-face))

    (,(concat "^[[:space:]]*\\(exit\\)[[:space:]]+\\("
              muselang--identifier-regexp
              "\\)[[:space:]]+\\(to\\)[[:space:]]+\\("
              muselang--identifier-regexp
              "\\)\\(?:[[:space:]]+\\(via\\)[[:space:]]+\\("
              muselang--identifier-regexp
              "\\)\\)?")
     (1 font-lock-keyword-face)
     (2 font-lock-function-name-face)
     (3 font-lock-keyword-face)
     (4 font-lock-type-face)
     (5 font-lock-keyword-face nil t)
     (6 font-lock-variable-name-face nil t))

    (,(concat "^[[:space:]]*\\(desc\\|description\\|say\\|hint\\)\\_>"
              "\\(?:[[:space:]]+\\(random\\)\\_>\\)?")
     (1 font-lock-keyword-face)
     (2 font-lock-builtin-face nil t))

    (,(regexp-opt muselang-property-keywords 'symbols)
     . font-lock-builtin-face)
    (,(regexp-opt muselang-control-keywords 'symbols)
     . font-lock-keyword-face)
    (,(regexp-opt muselang-word-operators 'symbols)
     . font-lock-keyword-face)
    (,(regexp-opt muselang-boolean-literals 'symbols)
     . font-lock-constant-face)
    ("\\_<-?[0-9]+\\(?:\\.[0-9]+\\)?\\_>" . font-lock-constant-face)
    ("==\\|!=\\|>=\\|<=\\|->\\|+=\\|-=\\|=" . font-lock-keyword-face))
  "Font lock rules for `muselang-mode'.")

(defvar muselang-mode-syntax-table
  (let ((table (make-syntax-table)))
    (modify-syntax-entry ?# "<" table)
    (modify-syntax-entry ?\n ">" table)
    (modify-syntax-entry ?\" "\"" table)
    (modify-syntax-entry ?_ "w" table)
    (modify-syntax-entry ?. "w" table)
    table)
  "Syntax table for `muselang-mode'.")

(defconst muselang--block-starter-regexp
  (concat "^[[:space:]]*"
          (regexp-opt
           '("room" "type" "object" "obj" "character" "char" "rule"
             "verb" "dialogue" "node" "goal" "time" "exit" "desc"
             "description" "say" "hint" "if" "elif" "else" "while"
             "until")
           'symbols))
  "Lines that commonly introduce an indented MuseLang block.")

(defun muselang--previous-code-line ()
  "Move to the previous nonblank, noncomment line.
Return non-nil if such a line exists."
  (let ((found nil))
    (while (and (not found) (= (forward-line -1) 0))
      (back-to-indentation)
      (unless (or (eolp) (looking-at-p "#"))
        (setq found t)))
    found))

(defun muselang--line-opens-block-p ()
  "Return non-nil when the current line appears to open a block."
  (save-excursion
    (back-to-indentation)
    (and (looking-at-p muselang--block-starter-regexp)
         (not (looking-at-p "else\\_>.*[^[:space:]]")))))

(defun muselang-calculate-indentation ()
  "Calculate indentation for the current MuseLang line."
  (save-excursion
    (beginning-of-line)
    (cond
     ((bobp) 0)
     ((looking-at-p "^[[:space:]]*$")
      (if (muselang--previous-code-line)
          (current-indentation)
        0))
     (t
      (let ((current-token
             (save-excursion
               (back-to-indentation)
               (thing-at-point 'symbol t))))
        (if (not (muselang--previous-code-line))
            0
          (let ((previous-indent (current-indentation))
                (previous-opens-block (muselang--line-opens-block-p)))
            (cond
             ((member current-token '("elif" "else"))
              (max 0 (- previous-indent
                        (if previous-opens-block muselang-indent-offset 0))))
             (previous-opens-block
              (+ previous-indent muselang-indent-offset))
             (t previous-indent)))))))))

(defun muselang-indent-line ()
  "Indent the current line according to MuseLang block structure."
  (interactive)
  (let ((column (- (current-column) (current-indentation)))
        (indent (muselang-calculate-indentation)))
    (indent-line-to indent)
    (when (> column 0)
      (move-to-column (+ indent column)))))

(defvar muselang-imenu-generic-expression
  `(("Rooms" ,(concat "^[[:space:]]*room[[:space:]]+\\("
                      muselang--identifier-regexp "\\)") 1)
    ("Objects" ,(concat "^[[:space:]]*\\(?:obj\\|object\\)[[:space:]]+\\("
                        muselang--identifier-regexp "\\)") 1)
    ("Characters" ,(concat "^[[:space:]]*\\(?:char\\|character\\)[[:space:]]+\\("
                           muselang--identifier-regexp "\\)") 1)
    ("Rules" ,(concat "^[[:space:]]*rule[[:space:]]+\\(.*\\)$") 1)
    ("Verbs" ,(concat "^[[:space:]]+verb[[:space:]]+\\("
                      muselang--identifier-regexp "\\)") 1)
    ("Dialogue" ,(concat "^[[:space:]]+\\(?:dialogue\\|node\\)[[:space:]]+\\("
                         muselang--identifier-regexp "\\)") 1))
  "Imenu expressions for MuseLang declarations.")

(defun muselang--skeleton-read (prompt default)
  "Read a skeleton field using PROMPT and DEFAULT."
  (let ((value (skeleton-read prompt)))
    (if (string-empty-p value) default value)))

(define-skeleton muselang-insert-room
  "Insert a MuseLang room block."
  nil
  "room " (muselang--skeleton-read "Room id: " "room_id")
  " \"" (muselang--skeleton-read "Display name: " "Display Name") "\"" \n
  "  desc" \n
  "    \"" _ "Room description.\"" \n)

(define-skeleton muselang-insert-object
  "Insert a MuseLang object block."
  nil
  "object " (muselang--skeleton-read "Object id: " "object_id")
  " in " (muselang--skeleton-read "Room id: " "room_id")
  " \"" (muselang--skeleton-read "Display name: " "Display Name") "\"" \n
  "  alias " (muselang--skeleton-read "Alias: " "alias") \n
  "  desc" \n
  "    \"" _ "Object description.\"" \n)

(define-skeleton muselang-insert-character
  "Insert a MuseLang character block."
  nil
  "character " (muselang--skeleton-read "Character id: " "character_id")
  " in " (muselang--skeleton-read "Room id: " "room_id")
  " \"" (muselang--skeleton-read "Display name: " "Display Name") "\"" \n
  "  alias " (muselang--skeleton-read "Alias: " "alias") \n
  "  desc" \n
  "    \"" _ "Character description.\"" \n)

(define-skeleton muselang-insert-exit
  "Insert a MuseLang exit block."
  nil
  "exit " (muselang--skeleton-read "Exit id: " "exit_id")
  " to " (muselang--skeleton-read "Destination room id: " "destination_room_id") \n
  "  alias " _ \n)

(define-skeleton muselang-insert-description
  "Insert a multiline MuseLang description block."
  nil
  "desc" \n
  "  \"" _ "Description line 1.\"" \n
  "  \"Description line 2.\"" \n)

(define-skeleton muselang-insert-say
  "Insert a multiline MuseLang say block."
  nil
  "say" \n
  "  \"" _ "Speech line 1.\"" \n
  "  \"Speech line 2.\"" \n)

(define-skeleton muselang-insert-hint
  "Insert a multiline MuseLang hint block."
  nil
  "hint" \n
  "  \"" _ "Hint line 1.\"" \n
  "  \"Hint line 2.\"" \n)

(define-skeleton muselang-insert-verb
  "Insert a MuseLang verb block."
  nil
  "verb " (muselang--skeleton-read "Verb name: " "verb_name") \n
  "  alias " (muselang--skeleton-read "Alias: " "alias") \n
  "  if " (muselang--skeleton-read "Condition: " "condition") \n
  "    say \"" _ "What happens.\"" \n)

(defvar muselang-mode-map
  (let ((map (make-sparse-keymap)))
    (define-key map (kbd "C-c C-r") #'muselang-insert-room)
    (define-key map (kbd "C-c C-o") #'muselang-insert-object)
    (define-key map (kbd "C-c C-c") #'muselang-insert-character)
    (define-key map (kbd "C-c C-e") #'muselang-insert-exit)
    (define-key map (kbd "C-c C-d") #'muselang-insert-description)
    (define-key map (kbd "C-c C-s") #'muselang-insert-say)
    (define-key map (kbd "C-c C-h") #'muselang-insert-hint)
    (define-key map (kbd "C-c C-v") #'muselang-insert-verb)
    map)
  "Keymap for `muselang-mode'.")

(defun muselang--diagnostic-region (source-buffer line)
  "Return a Flymake diagnostic region in SOURCE-BUFFER for LINE.
LINE is one based, as reported by the MuseLang linter."
  (with-current-buffer source-buffer
    (save-restriction
      (widen)
      (goto-char (point-min))
      (forward-line (max 0 (1- line)))
      (cons (line-beginning-position) (line-end-position)))))

(defun muselang--parse-lint-output (source-buffer output)
  "Convert MuseLang JSON lint OUTPUT into Flymake diagnostics.
SOURCE-BUFFER is the buffer being checked."
  (let ((json-object-type 'alist)
        (json-array-type 'list)
        (json-key-type 'symbol)
        diagnostics)
    (condition-case err
        (let* ((payload (json-read-from-string output))
               (items (alist-get 'diagnostics payload)))
          (dolist (item items)
            (let* ((line (max 1 (or (alist-get 'line item) 1)))
                   (message (or (alist-get 'message item) "MuseLang lint error"))
                   (severity (if (equal (alist-get 'severity item) "warning")
                                 :warning
                               :error))
                   (region (muselang--diagnostic-region source-buffer line)))
              (push (flymake-make-diagnostic
                     source-buffer (car region) (cdr region) severity message)
                    diagnostics))))
      (error
       (push (flymake-make-diagnostic
              source-buffer (point-min) (min (1+ (point-min)) (point-max))
              :error
              (format "Could not parse MuseLang lint output: %s"
                      (error-message-string err)))
             diagnostics)))
    (nreverse diagnostics)))

(defun muselang-flymake-backend (report-fn &rest _args)
  "Flymake backend for the MuseLang command line linter.
REPORT-FN is supplied by Flymake."
  (if (not (executable-find muselang-linter-command))
      (funcall report-fn nil)
    (let* ((source-buffer (current-buffer))
         (extension (or (file-name-extension (or buffer-file-name "")) "muse"))
         (temp-file (make-temp-file "muselang-flymake-" nil
                                    (concat "." extension)))
         (output-buffer (generate-new-buffer " *muselang-flymake*")))
    (write-region nil nil temp-file nil 'silent)
    (make-process
     :name "muselang-flymake"
     :buffer output-buffer
     :command (list muselang-linter-command "lint" temp-file)
     :noquery t
     :connection-type 'pipe
     :sentinel
     (lambda (process _event)
       (when (memq (process-status process) '(exit signal))
         (unwind-protect
             (when (buffer-live-p source-buffer)
               (with-current-buffer output-buffer
                 (let ((output (string-trim (buffer-string))))
                   (funcall report-fn
                            (if (string-empty-p output)
                                (list (flymake-make-diagnostic
                                       source-buffer
                                       (with-current-buffer source-buffer (point-min))
                                       (with-current-buffer source-buffer
                                         (min (1+ (point-min)) (point-max)))
                                       :error
                                       "MuseLang linter returned no output"))
                              (muselang--parse-lint-output
                               source-buffer output))))))
           (ignore-errors (delete-file temp-file))
           (kill-buffer output-buffer))))))))

(defun muselang--enable-flymake ()
  "Enable Flymake support for the current MuseLang buffer when possible."
  (when (and muselang-enable-flymake
             (require 'flymake nil t)
             (executable-find muselang-linter-command))
    (add-hook 'flymake-diagnostic-functions
              #'muselang-flymake-backend nil t)
    (flymake-mode 1)))

;;;###autoload
(define-derived-mode muselang-mode prog-mode "MuseLang"
  "Major mode for editing MuseLang V1 source files."
  :syntax-table muselang-mode-syntax-table
  (setq-local font-lock-defaults '(muselang-font-lock-keywords))
  (setq-local indent-line-function #'muselang-indent-line)
  (setq-local comment-start "# ")
  (setq-local comment-start-skip "#+[[:space:]]*")
  (setq-local comment-end "")
  (setq-local tab-width muselang-indent-offset)
  (setq-local indent-tabs-mode nil)
  (setq-local imenu-generic-expression muselang-imenu-generic-expression)
  (setq-local electric-indent-chars '(?\n))
  (setq-local electric-pair-pairs
              '((?\" . ?\") (?( . ?)) (?[ . ?]) (?{ . ?})))
  (setq-local electric-pair-text-pairs '((?\" . ?\")))
  (electric-pair-local-mode 1)
  (muselang--enable-flymake))

;;;###autoload
(add-to-list 'auto-mode-alist '("\\.muse\\'" . muselang-mode))

;;;###autoload
(add-to-list 'auto-mode-alist '("\\.muselang\\'" . muselang-mode))

(provide 'muselang-mode)

;;; muselang-mode.el ends here
