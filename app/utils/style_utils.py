import os
import tinycss2
import cssmin
import logging
import argparse
#run python app/utils/style_utils.py app/static app/static/styles.min.css
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def merge_css_files(directory, output_file):
    css_rules = {}

    if os.path.exists(output_file):
        overwrite = input(f"{output_file} already exists. Overwrite? (y/n): ")
        if overwrite.lower() != "y":
            logging.warning("Operation cancelled.")
            return

    for root, _, files in os.walk(directory):
        for filename in sorted(files):
            if filename.endswith(".css"):
                filepath = os.path.join(root, filename)
                logging.info(f"Processing {filepath}...")

                try:
                    with open(filepath, "r", encoding="utf-8") as file:
                        css_content = file.read()

                    minified_css = cssmin.cssmin(css_content)

                    parsed_rules = tinycss2.parse_stylesheet(minified_css, skip_comments=True, skip_whitespace=True)

                    for rule in parsed_rules:
                        if rule.type == "qualified-rule":
                            selector = "".join(token.serialize() for token in rule.prelude).strip()
                            declarations = "".join(token.serialize() for token in rule.content).strip()

                            if selector in css_rules:
                                css_rules[selector].append(declarations)
                            else:
                                css_rules[selector] = [declarations]

                except FileNotFoundError:
                    logging.error(f"File not found: {filepath}")
                except IOError as e:
                    logging.error(f"Error reading file {filepath}: {e}")
                except Exception as e:
                    logging.error(f"Unexpected error processing {filepath}: {e}")

    try:
        with open(output_file, "w", encoding="utf-8") as output:
            for selector, declarations_list in css_rules.items():
                combined_declarations = "; ".join(declarations_list)
                output.write(f"{selector} {{{combined_declarations}}}\n")

        logging.info(f"CSS files merged and saved as '{output_file}'.")
    except IOError as e:
        logging.error(f"Error writing to {output_file}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge CSS files in a directory.")
    parser.add_argument("directory", help="Directory containing CSS files")
    parser.add_argument("output_file", help="Output file for merged CSS")
    args = parser.parse_args()

    merge_css_files(args.directory, args.output_file)