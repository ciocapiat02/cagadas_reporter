OUTPUT_HTML=output/cagadas_report.html
OUTPUT_PDF=output/cagadas_report.pdf
OUTPUT_RELEASE=output/release.html
INPUT_FILE=output/cagadas_report.md

html: $(INPUT_FILE)
	cd output
	python cagadas.py
	pandoc --katex -s $(INPUT_FILE) -o $(OUTPUT_HTML) --from gfm --toc
	cd ..

pdf: $(INPUT_FILE) html
	cd output
	# cp my-style.css output/my-style.css
	pandoc --katex --pdf-engine weasyprint -s $(INPUT_FILE) -o $(OUTPUT_PDF) --from gfm --css=output/my-style.css --embed-resources --toc --variable=geometry:margin=0in
	cd ..

release: $(INPUT_FILE)
	cd output
	if [ ! -d release ]; then mkdir release; fi
	pandoc -t revealjs -s $(INPUT_FILE) -o $(OUTPUT_RELEASE) --from gfm --embed-resources --toc
	cd ..

clean:
	cd output
	if [ -d release ];then rm -r release; fi
	if [ -e $(OUTPUT_HTML) ];then rm $(OUTPUT_HTML); fi
	cd ..

open: $(OUTPUT_HTML) html
	cd output
	librewolf $(OUTPUT_HTML)
	cd ..

open-pdf: $(OUTPUT_PDF) pdf
	cd output
	librewolf $(OUTPUT_PDF)
	cd ..
