import os
import re
import email
from email import policy
from email.parser import BytesParser
import pytz

class EmlFileRenamer:
    def __init__(self, directory):
        self.directory = directory

    def sanitize_subject(self, subject):
        """Sanitize the email subject for use in a filename."""
        # Initial cleanup and replacement of invalid filename characters
        subject = re.sub(r'[<>:"/\\|?*]', '_', subject.strip())
        subject = re.sub(r'(:\s*|-\s*)', '_', subject)
        subject = subject.rstrip('.').rstrip('!')
        subject = re.sub(r'_{2,}', '_', subject)

        # Special case for "You've" at the start of the subject
        if subject.startswith("You've"):
            subject = subject.replace("You've", "You_have", 1)

        # Define general replacements
        replacements = {
            'Order ID': 'OrderID',
            '&': 'and',
            ',': '_',
            'you’ve': 'you_have',
            '#': '',
        }
        for old, new in replacements.items():
            subject = subject.replace(old, new)

        # Handle specific terms with dots that should be preserved
        protected_terms = ["Mi.com", "Amazon.in"]
        for term in protected_terms:
            subject = subject.replace(term, term.replace('.', '[DOT]'))

        # Temporarily replace currency values with placeholders to preserve dots
        currency_pattern = r'₹\d+\.\d{2}'
        currency_matches = re.findall(currency_pattern, subject)
        for match in currency_matches:
            subject = subject.replace(match, match.replace('.', '[CUR_DOT]'))

        # Remove remaining dots from the subject
        subject = subject.replace('.', '')

        # Restore the protected terms and currency values
        subject = subject.replace('[DOT]', '.')
        subject = subject.replace('[CUR_DOT]', '.')

        # Additional cleanup to remove any unexpected characters like BOM or tabs
        subject = subject.encode('ascii', 'ignore').decode()  # Remove non-ASCII chars
        subject = re.sub(r'\s+', ' ', subject).strip()  # Replace multiple spaces/tabs with a single space

        return subject

    def clean_filename(self, filename):
        """Clean the filename by removing trailing dots and extra underscores."""
        filename = re.sub(r'_{2,}', '_', filename)
        return filename.rstrip('.')

    def is_correct_format(self, filename, formatted_date, subject):
        """Check if the filename matches the expected format."""
        normalized_subject = re.sub(r'_{2,}', '_', subject)
        pattern = rf"^{formatted_date} {re.escape(normalized_subject)}\.eml$"
        return re.match(pattern, filename) is not None

    def rename_eml_file(self, file_path):
        """Rename a single .eml file based on its date and subject."""
        with open(file_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)

        date_header = msg.get('Date')
        subject = msg.get('Subject', 'No Subject').strip()

        subject = self.sanitize_subject(subject).replace(" ", "_")
        
        if date_header:
            try:
                date_obj = email.utils.parsedate_to_datetime(date_header)
                utc = pytz.UTC
                target_timezone = pytz.timezone("Asia/Kolkata")
                date_obj = date_obj.astimezone(utc).astimezone(target_timezone)
                formatted_date = date_obj.strftime('%Y-%m-%dT%H_%M_%S')
            except (ValueError, TypeError):
                formatted_date = "Unknown_Date"
        else:
            formatted_date = "Unknown_Date"

        new_filename = f"{formatted_date} {subject}.eml"
        new_filename = self.clean_filename(new_filename)

        new_file_path = os.path.join(os.path.dirname(file_path), new_filename)

        if not self.is_correct_format(os.path.basename(file_path), formatted_date, subject):
            try:
                os.rename(file_path, new_file_path)
                print(f"Renamed '{os.path.basename(file_path)}' to '{new_filename}'")
            except OSError as e:
                print(f"Error renaming '{os.path.basename(file_path)}': {e}")
        else:
            print(f"Skipped renaming for '{os.path.basename(file_path)}' (already in correct format)")

    def rename_eml_files(self):
        """Rename all .eml files in the specified directory."""
        if os.path.isdir(self.directory):
            for filename in os.listdir(self.directory):
                if filename.endswith('.eml'):
                    file_path = os.path.join(self.directory, filename)
                    self.rename_eml_file(file_path)
        elif os.path.isfile(self.directory) and self.directory.endswith('.eml'):
            self.rename_eml_file(self.directory)
        else:
            print("Invalid path. Please provide a directory or a .eml file path.")


# Specify the path to a directory or a single .eml file
directory = r'C:\Users\hp\Downloads\Email\edit'
renamer = EmlFileRenamer(directory)
renamer.rename_eml_files()
