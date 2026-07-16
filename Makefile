.PHONY: install serve clean update-fipe

# Install dependencies for the Jekyll website
install:
	@echo "Installing Jekyll dependencies in website/..."
	cd website && bundle install

# Start local dev server
serve:
	@echo "Starting local Jekyll server..."
	cd website && bundle exec jekyll serve

# Run FIPE pricing database updater
update-fipe:
	@echo "Updating FIPE prices for all manufacturers..."
	python3 scripts/fipe_updater.py

# Cleanup build artifacts
clean:
	@echo "Cleaning Jekyll site and caches..."
	cd website && rm -rf _site .jekyll-cache Gemfile.lock
