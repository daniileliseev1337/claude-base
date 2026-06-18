;; ============================================================
;; GCH W-layer: ACAD_TABLE builder from data file. Single + multi-column.
;; Reads C:/temp/table_data.txt (cp1251). Pure-ASCII source.
;; Data file (TAB-separated):
;;   LAYOUT<TAB>name | INS<TAB>x<TAB>y | COLS<TAB>w1<TAB>w2... | NROWS<TAB>n
;;   STYLE<TAB>ts | THMAX<TAB>h | MARGIN<TAB>m | TARGETH<TAB>h
;;   GAP<TAB>g | XSTART<TAB>x | YTOP<TAB>y | MAXCOLS<TAB>n        (multi only)
;;   ROW<TAB>idx<TAB>type<TAB>cell1<TAB>cell2...   type: title|header|section|data
;; Entry: (c7:build) single column auto-fit ; (c7:build-multi) auto-split columns
;; ============================================================

(vl-load-com)

(defun c7:split (str sep / pos res)
  (setq res '())
  (while (setq pos (vl-string-search sep str))
    (setq res (cons (substr str 1 pos) res))
    (setq str (substr str (+ pos 1 (strlen sep)))))
  (reverse (cons str res)))

(defun c7:get-block (lname / blk)
  (setq blk nil)
  (vlax-for lo (vla-get-Layouts (vla-get-ActiveDocument (vlax-get-acad-object)))
    (if (= (vla-get-Name lo) lname) (setq blk (vla-get-Block lo))))
  blk)

(defun c7:safe (fn args) (vl-catch-all-apply fn args))

(defun c7:safe-del (h / o)
  (setq o (vl-catch-all-apply 'vla-HandleToObject
            (list (vla-get-ActiveDocument (vlax-get-acad-object)) h)))
  (if (and o (not (vl-catch-all-error-p o)))
    (vl-catch-all-apply 'vla-Delete (list o))))

;; build a table from a list of rows (each: (type cell1 cell2 ...)); returns table obj
(defun c7:build-list (rowlist insx insy th / blk tbl n i rd rtype c cci rri rowmin)
  (setq n (length rowlist) blk (c7:get-block GC:LNAME))
  (setvar "CTABLESTYLE" "Standard")
  (setq tbl (vla-AddTable blk (vlax-3d-point insx insy 0.0) n GC:NCOLS 10.0 50.0))
  (vla-put-RegenerateTableSuppressed tbl :vlax-true)
  (vla-put-VertCellMargin tbl GC:MARGIN)
  (vla-put-HorzCellMargin tbl GC:MARGIN)
  (setq i 0) (foreach w GC:COLS (vla-SetColumnWidth tbl i w) (setq i (1+ i)))
  ;; ACAD auto-merges row 0 as a title; unmerge every row so header cells survive
  (setq rri 0) (while (< rri n) (c7:safe 'vla-UnmergeCells (list tbl rri rri 0 (1- GC:NCOLS))) (setq rri (1+ rri)))
  (setq rri 0)
  (foreach rd rowlist
    (setq rtype (car rd) c (cdr rd))
    (cond
      ((or (= rtype "title") (= rtype "section"))
        (c7:safe 'vla-MergeCells (list tbl rri rri 0 (1- GC:NCOLS)))
        (vla-SetText tbl rri 0 (car c)))
      (t (setq i 0) (foreach cell c (if (< i GC:NCOLS) (vla-SetText tbl rri i cell)) (setq i (1+ i)))))
    (setq rri (1+ rri)))
  (setq rri 0)
  (while (< rri n)
    (setq cci 0)
    (while (< cci GC:NCOLS)
      (c7:safe 'vla-SetCellTextStyle (list tbl rri cci GC:STYLE))
      (c7:safe 'vla-SetCellTextHeight (list tbl rri cci th))
      (setq cci (1+ cci)))
    (setq rri (1+ rri)))
  (setq rowmin (+ (* th 1.4) (* 2.0 GC:MARGIN)) rri 0)
  (while (< rri n) (c7:safe 'vla-SetRowHeight (list tbl rri rowmin)) (setq rri (1+ rri)))
  (setq rri 0)
  (foreach rd rowlist
    (setq rtype (car rd))
    (if (= rtype "data")
      (progn (vla-SetCellAlignment tbl rri 0 5)
             (if (> GC:NCOLS 1) (vla-SetCellAlignment tbl rri 1 4))
             (setq cci 2) (while (< cci GC:NCOLS) (vla-SetCellAlignment tbl rri cci 5) (setq cci (1+ cci))))
      (progn (setq cci 0) (while (< cci GC:NCOLS) (vla-SetCellAlignment tbl rri cci 5) (setq cci (1+ cci)))))
    (setq rri (1+ rri)))
  (vla-put-RegenerateTableSuppressed tbl :vlax-false)
  tbl)

(defun c7:tbl-height (tbl)
  (vla-GetBoundingBox tbl 'mn 'mx)
  (- (cadr (vlax-safearray->list mx)) (cadr (vlax-safearray->list mn))))

(defun c7:read-data ( / f line tab parts key)
  (setq tab (chr 9) GC:ROWS '() GC:GAP 4.0 GC:MAXCOLS 4 GC:QTYCOL nil)
  (setq f (open "C:/temp/table_data.txt" "r"))
  (while (setq line (read-line f))
    (setq parts (c7:split line tab) key (car parts))
    (cond
      ((= key "LAYOUT")  (setq GC:LNAME (cadr parts)))
      ((= key "INS")     (setq GC:INSX (atof (cadr parts)) GC:INSY (atof (caddr parts))))
      ((= key "COLS")    (setq GC:COLS (mapcar 'atof (cdr parts))))
      ((= key "NROWS")   (setq GC:NROWS (atoi (cadr parts))))
      ((= key "STYLE")   (setq GC:STYLE (cadr parts)))
      ((= key "THMAX")   (setq GC:THMAX (atof (cadr parts))))
      ((= key "MARGIN")  (setq GC:MARGIN (atof (cadr parts))))
      ((= key "TARGETH") (setq GC:TARGETH (atof (cadr parts))))
      ((= key "QTYCOL")  (setq GC:QTYCOL (atoi (cadr parts))))
      ((= key "GAP")     (setq GC:GAP (atof (cadr parts))))
      ((= key "XSTART")  (setq GC:XSTART (atof (cadr parts))))
      ((= key "YTOP")    (setq GC:YTOP (atof (cadr parts))))
      ((= key "MAXCOLS") (setq GC:MAXCOLS (atoi (cadr parts))))
      ((= key "ROW")     (setq GC:ROWS (cons (cddr parts) GC:ROWS)))))   ; (type cell...)
  (close f)
  (setq GC:ROWS (reverse GC:ROWS) GC:NCOLS (length GC:COLS)
        GC:COLW (apply '+ GC:COLS)))

;; --- single column, auto-fit text height to TARGETH ---
(defun c7:build ( / lo hi mid iter tbl H best prevh)
  (c7:read-data)
  (setq lo 0.8 hi GC:THMAX best 0.8 iter 0 prevh nil)
  (while (< iter 7)
    (setq mid (/ (+ lo hi) 2.0))
    (if prevh (c7:safe-del prevh))
    (setq tbl (c7:build-list GC:ROWS GC:INSX GC:INSY mid) H (c7:tbl-height tbl) prevh (vla-get-Handle tbl))
    (if (<= H GC:TARGETH) (setq lo mid best mid) (setq hi mid))
    (setq iter (1+ iter)))
  (if prevh (c7:safe-del prevh))
  (setq tbl (c7:build-list GC:ROWS GC:INSX GC:INSY best) G:LASTTABLE (vla-get-Handle tbl))
  (princ (strcat "BUILT th=" (rtos best 2 2) " H=" (rtos (c7:tbl-height tbl) 2 1))))

;; measure per-row heights at given th (builds a throwaway table far away)
(defun c7:measure-heights (th / tbl hs i n)
  (setq tbl (c7:build-list GC:ROWS -99000.0 0.0 th) n GC:NROWS i 0 hs '())
  (while (< i n) (setq hs (cons (vla-GetRowHeight tbl i) hs)) (setq i (1+ i)))
  (vla-Delete tbl)
  (reverse hs))

;; greedy split of data/section rows (idx 2..n-1) into columns of height <= target.
;; title(0)+header(1) repeated atop each column. moves hanging section to next col.
;; returns list of index-lists.
(defun c7:layout-cols (hs target / n base i hi cols cur curh lastix moved)
  (setq n (length hs) base (+ (nth 0 hs) (nth 1 hs)) cols '() cur '() curh base i 2)
  (while (< i n)
    (setq hi (nth i hs))
    (if (and cur (> (+ curh hi) target))
      (progn
        (setq lastix (car (reverse cur)))
        (if (= "section" (car (nth lastix GC:ROWS)))
          (progn (setq moved lastix cur (reverse (cdr (reverse cur))))
                 (setq cols (append cols (list cur)) cur (list moved) curh (+ base (nth moved hs))))
          (setq cols (append cols (list cur)) cur '() curh base))))
    (setq cur (append cur (list i)) curh (+ curh hi) i (1+ i)))
  (if cur (setq cols (append cols (list cur))))
  cols)

;; --- multi column, auto-split + auto-fit so columns <= MAXCOLS ---
(defun c7:build-multi ( / lo hi mid iter hs collist ncols best k idxs subset insx tbl nk x0 base tbal)
  (c7:read-data)
  (setq lo 0.8 hi GC:THMAX best 0.8 iter 0)
  (while (< iter 6)
    (setq mid (/ (+ lo hi) 2.0))
    (setq hs (c7:measure-heights mid) collist (c7:layout-cols hs GC:TARGETH) ncols (length collist))
    (if (<= ncols GC:MAXCOLS) (setq lo mid best mid) (setq hi mid))
    (setq iter (1+ iter)))
  (setq hs (c7:measure-heights best) collist (c7:layout-cols hs GC:TARGETH))
  (setq nk (length collist))
  ;; balance: redistribute rows evenly across nk columns
  (if (> nk 1)
    (progn
      (setq base (+ (nth 0 hs) (nth 1 hs)))
      (setq tbal (/ (+ (- (apply '+ hs) base) (* nk base)) (float nk)))
      (setq collist (c7:layout-cols hs (* tbal 1.06)) nk (length collist))))
  ;; right-anchored block: left edge so the K columns end at XRIGHT (=GC:XSTART)
  (setq x0 (- GC:XSTART (* nk GC:COLW) (* (1- nk) GC:GAP)))
  (setq k 0 G:TABLES '())
  (foreach idxs collist
    (setq subset (list (nth 0 GC:ROWS) (nth 1 GC:ROWS)))
    (foreach ix idxs (setq subset (append subset (list (nth ix GC:ROWS)))))
    (setq insx (+ x0 (* k (+ GC:COLW GC:GAP))))
    (setq tbl (c7:build-list subset insx GC:YTOP best))
    (setq G:TABLES (cons (vla-get-Handle tbl) G:TABLES) k (1+ k)))
  (princ (strcat "MULTI cols=" (itoa (length collist)) " th=" (rtos best 2 2))))

;; --- verification: dump (pos : last-column) pairs from built tables to a file ---
;; reads G:TABLES (multi) or G:LASTTABLE (single). Python then cross-checks vs xlsx.
(defun c7:verify-dump ( / doc s tbl nr nc r n0 f hs qc)
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)) s "")
  (setq hs (if G:TABLES G:TABLES (if G:LASTTABLE (list G:LASTTABLE) '())))
  (foreach h hs
    (setq tbl (vla-HandleToObject doc h) nr (vla-get-Rows tbl) nc (vla-get-Columns tbl) r 0)
    (setq qc (if GC:QTYCOL (1- GC:QTYCOL) (1- nc)))        ; 0-based qty column
    (while (< r nr)
      (setq n0 (vla-GetText tbl r 0))
      (if (and (> (strlen n0) 0) (> (atoi n0) 0) (= n0 (itoa (atoi n0))))
        (setq s (strcat s n0 ":" (vla-GetText tbl r qc) " ")))
      (setq r (1+ r))))
  (setq f (open "C:/temp/acad_pairs.txt" "w")) (write-line s f) (close f)
  (princ "verify pairs -> C:/temp/acad_pairs.txt"))

(princ "gen_table.lsp loaded: (c7:build) | (c7:build-multi) | (c7:verify-dump)")
(princ)
