build-function:
	starting_path=$$(pwd); \
	cd function; \
	absolute_root_path=$$(pwd); \
	rm function.zip; \
	pip3 install -r requirements.txt --target packages; \
	cd packages; \
	zip -r "$$absolute_root_path/function.zip" .; \
	cd $$absolute_root_path; \
	zip -Rg function.zip "*" -x "packages/*" "venv/*" "tests/*" "__pycache__/*" "**/__pycache__/*" ".idea/*" requirements.txt .DS_Store; \
	rm -rf packages; \
	cd $$starting_path;

deploy:
	npm install; \
	make build-function; \
	cdk deploy;