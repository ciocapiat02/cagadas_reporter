OUTPUT_HTML=cagadas_report.html
OUTPUT_PDF=cagadas_report.pdf
OUTPUT_RELEASE=release/release.html
INPUT_FILE=cagadas_report.md

html: $(INPUT_FILE)
	pandoc --katex -s $(INPUT_FILE) -o $(OUTPUT_HTML) --from gfm --toc

pdf: $(INPUT_FILE)
	pandoc --katex --pdf-engine weasyprint -s $(INPUT_FILE) -o $(OUTPUT_PDF) --from gfm --embed-resources --toc

release: $(INPUT_FILE)
	if [ ! -d release ]; then mkdir release; fi
	pandoc -t revealjs -s $(INPUT_FILE) -o $(OUTPUT_RELEASE) --from gfm --embed-resources --toc

clean:
	if [ -d release ];then rm -r release; fi
	if [ -e $(OUTPUT_HTML) ];then rm $(OUTPUT_HTML); fi

open: $(OUTPUT_HTML)
	xdg-open $(OUTPUT_HTML)
