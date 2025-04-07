from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import re
import io
from typing import Dict, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    # Allow all origins for network access (you can restrict this to specific IPs if needed)
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def redact_sensitive_info(text: str) -> Tuple[str, Dict[str, int]]:
    # Create a copy of the original text
    redacted_text = text
    redaction_info = {}

    # Email regex pattern - more comprehensive
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    # Phone number patterns - multiple formats
    phone_patterns = [
        r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',  # Standard US format
        r'\b\d{3}[\s.-]?\d{4}\b',  # Last 7 digits
        r'\b\d{5}[\s.-]?\d{5,6}\b',  # International format
        r'\b\(\d{3}\)[\s.-]?\d{3}[\s.-]?\d{4}\b',  # (123) 456-7890
    ]

    # SSN patterns
    ssn_patterns = [
        r'\b\d{3}[-]?\d{2}[-]?\d{4}\b',  # Standard SSN
        r'\bSSN[:\s]+\d{3}[-]?\d{2}[-]?\d{4}\b',  # With SSN prefix
        r'\bSocial Security[:\s]+\d{3}[-]?\d{2}[-]?\d{4}\b',  # Full text
    ]

    # Credit card patterns
    cc_patterns = [
        r'\b(?:\d[ -]*?){13,16}\b',  # General pattern
        r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # 16-digit with separators
        r'\b\d{4}[- ]?\d{6}[- ]?\d{4}[- ]?\d{1}\b',  # AMEX format
    ]

    # Date patterns
    date_patterns = [
        r'\b(0?[1-9]|1[0-2])[\/-](0?[1-9]|[12]\d|3[01])[\/-](19|20)\d{2}\b',  # MM/DD/YYYY
        r'\b(19|20)\d{2}[\/-](0?[1-9]|1[0-2])[\/-](0?[1-9]|[12]\d|3[01])\b',  # YYYY/MM/DD
        r'\b(0?[1-9]|[12]\d|3[01])[\/-](0?[1-9]|1[0-2])[\/-](19|20)\d{2}\b',  # DD/MM/YYYY
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[\s.-]+(0?[1-9]|[12]\d|3[01])[\s,.-]+(19|20)\d{2}\b',  # Month DD, YYYY
    ]

    # Address patterns
    address_patterns = [
        r'\b\d+\s[A-Za-z0-9\s,]+\b(?:Avenue|Ave|Street|St|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Circle|Cir|Place|Pl)\b',
        r'\b\d+\s[A-Za-z0-9\s,]+,\s[A-Za-z\s]+,\s[A-Z]{2}\s\d{5}(-\d{4})?\b',  # Full address with city, state, zip
        r'\bP\.?O\.?\sBox\s\d+\b',  # PO Box
    ]

    # Name patterns - comprehensive person name detection
    name_patterns = [
        # Names with titles
        r'\b(Mr\.|Mrs\.|Ms\.|Dr\.|Miss|Prof\.|Sir|Lady|Lord|Madam|Rev\.|Capt\.|Lt\.|Sgt\.|Col\.)\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b',

        # Common first name + last name format (using common first names to reduce false positives)
        r'\b(John|Jane|David|Michael|Robert|Mary|William|James|Patricia|Jennifer|Linda|Elizabeth|Susan|Jessica|Sarah|Thomas|Charles|Karen|Daniel|Matthew|Anthony|Donald|Steven|Paul|Andrew|Mark|George|Richard|Kenneth|Edward|Christopher|Brian|Joseph|Kevin|Jason|Timothy|Jeffrey|Ryan|Jacob|Gary|Nicholas|Eric|Stephen|Jonathan|Larry|Justin|Scott|Brandon|Benjamin|Samuel|Gregory|Alexander|Patrick|Frank|Raymond|Jack|Dennis|Jerry|Tyler|Aaron|Jose|Adam|Nathan|Henry|Douglas|Zachary|Peter|Kyle|Walter|Ethan|Jeremy|Harold|Keith|Christian|Roger|Noah|Gerald|Carl|Terry|Sean|Austin|Arthur|Lawrence|Jesse|Dylan|Bryan|Joe|Jordan|Billy|Bruce|Albert|Willie|Gabriel|Logan|Alan|Juan|Wayne|Roy|Ralph|Randy|Eugene|Vincent|Russell|Elijah|Louis|Bobby|Philip|Johnny|Mary|Patricia|Jennifer|Linda|Elizabeth|Susan|Jessica|Sarah|Karen|Nancy|Lisa|Betty|Margaret|Sandra|Ashley|Kimberly|Emily|Donna|Michelle|Dorothy|Carol|Amanda|Melissa|Deborah|Stephanie|Rebecca|Sharon|Laura|Cynthia|Kathleen|Amy|Shirley|Angela|Helen|Anna|Brenda|Pamela|Nicole|Emma|Samantha|Katherine|Christine|Debra|Rachel|Catherine|Carolyn|Janet|Ruth|Maria|Heather|Diane|Virginia|Julie|Joyce|Victoria|Olivia|Kelly|Christina|Lauren|Joan|Evelyn|Judith|Megan|Cheryl|Andrea|Hannah|Martha|Jacqueline|Frances|Gloria|Ann|Teresa|Kathryn|Sara|Janice|Jean|Alice|Madison|Doris|Abigail|Julia|Judy|Grace|Denise|Amber|Marilyn|Beverly|Danielle|Theresa|Sophia|Marie|Diana|Brittany|Natalie|Isabella|Charlotte|Rose|Alexis|Kayla)\s[A-Z][a-z]+\b',

        # Last name, First name format
        r'\b[A-Z][a-z]+,\s[A-Z][a-z]+(?:\s[A-Z]\.)?\b',

        # Full name with middle initial
        r'\b[A-Z][a-z]+\s[A-Z]\.\s[A-Z][a-z]+\b',

        # Full name with middle name
        r'\b[A-Z][a-z]+\s[A-Z][a-z]+\s[A-Z][a-z]+\b',

        # Name with suffix
        r'\b[A-Z][a-z]+\s[A-Z][a-z]+(?:\s(Jr\.|Sr\.|I{1,3}|IV|V|VI|VII|VIII|IX|X))\b',

        # Names in context (e.g., "Name: John Smith")
        r'\b(?:Name|Full Name|Customer|Client|Patient|Employee|Student|Applicant|Recipient|Sender|Buyer|Seller|Owner|User|Member|Subscriber|Contact|Representative)\s*[:;-]\s*[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b',

        # Names in signature blocks
        r'\b(?:Sincerely|Regards|Best regards|Yours truly|Yours sincerely|Respectfully|Respectfully submitted|Yours faithfully|Thank you|Thanks|Best wishes),?\s*\n+\s*[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b',

        # Names with positions/titles
        r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2}\s*,\s*(?:CEO|CTO|CFO|COO|President|Vice President|Director|Manager|Supervisor|Administrator|Coordinator|Specialist|Analyst|Engineer|Developer|Consultant|Advisor|Associate|Assistant|Officer|Executive|Head|Lead|Chief|Senior|Junior)\b'
    ]

    # Company patterns
    company_patterns = [
        r'\b[A-Z][A-Za-z0-9\s,\.]+\b(?:Inc\.|LLC|Corp\.|Corporation|Ltd\.|Limited|Co\.|Company)\b',
        r'\b[A-Z][A-Za-z0-9\s,\.&]+\b(?:Group|Partners|Associates|Enterprises|Solutions|Technologies|Systems)\b',
    ]

    # Financial patterns
    financial_patterns = [
        r'\b\d{8,17}\b',  # Bank account numbers
        r'\bACH[:\s]+\d+\b',  # ACH numbers
        r'\bRouting[:\s]+\d{9}\b',  # Routing numbers
        r'\bAccount[:\s]+[\d\s-]+\b',  # Account numbers with prefix
    ]

    # ID patterns
    id_patterns = [
        r'\b[A-Z]{1,2}\d{6,9}\b',  # Passport numbers
        r'\b\d{2}[-]?\d{7}\b',  # Driver's license (some formats)
        r'\bID[:\s]+[A-Z0-9-]+\b',  # Generic ID numbers
    ]

    # Network patterns
    network_patterns = [
        r'\b(?:\d{1,3}\.){3}\d{1,3}\b',  # IPv4
        r'\b([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b',  # IPv6
        r'\b([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})\b',  # MAC address
    ]

    # Helper function to apply multiple patterns
    def apply_patterns(patterns, replacement, label):
        nonlocal redacted_text
        count = 0
        for pattern in patterns:
            try:
                matches = re.findall(pattern, text)
                count += len(matches)
                redacted_text = re.sub(pattern, replacement, redacted_text)
            except Exception as e:
                logging.error(f"Error applying pattern {pattern} for {label}: {str(e)}")
                # Continue with other patterns even if one fails
        redaction_info[label] = count
        return count

    # Apply all pattern groups
    # Email redaction
    redacted_text = re.sub(email_pattern, '[EMAIL REDACTED]', redacted_text)
    redaction_info['emails'] = len(re.findall(email_pattern, text))

    # Phone number redaction
    apply_patterns(phone_patterns, '[PHONE REDACTED]', 'phones')

    # SSN redaction
    apply_patterns(ssn_patterns, '[SSN REDACTED]', 'ssn')

    # Credit card redaction
    apply_patterns(cc_patterns, '[CREDIT CARD REDACTED]', 'credit_cards')

    # Date redaction
    apply_patterns(date_patterns, '[DATE REDACTED]', 'dates')

    # Address redaction
    apply_patterns(address_patterns, '[ADDRESS REDACTED]', 'addresses')

    # Name redaction
    apply_patterns(name_patterns, '[NAME REDACTED]', 'names')

    # Company redaction
    apply_patterns(company_patterns, '[COMPANY REDACTED]', 'companies')

    # Financial information redaction
    apply_patterns(financial_patterns, '[FINANCIAL INFO REDACTED]', 'financial')

    # ID redaction
    apply_patterns(id_patterns, '[ID REDACTED]', 'ids')

    # Network information redaction
    apply_patterns(network_patterns, '[NETWORK INFO REDACTED]', 'network')

    return redacted_text, redaction_info

@app.post("/api/redact-pdf")
async def redact_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        return {"error": "Only PDF files are allowed"}

    try:
        logging.info(f"Processing file: {file.filename}")
        # Read the uploaded file
        pdf_content = await file.read()
        pdf_file = io.BytesIO(pdf_content)

        # Process PDF
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        redacted_text = []
        redaction_stats = []
        total_redactions = {}

        logging.info(f"PDF has {len(pdf_reader.pages)} pages")

        # Extract and redact text from each page
        for i, page in enumerate(pdf_reader.pages):
            try:
                logging.info(f"Processing page {i+1}")
                text = page.extract_text()
                if not text:
                    logging.warning(f"No text extracted from page {i+1}")
                    redacted_text.append("[No text could be extracted from this page]")
                    redaction_stats.append({})
                    continue

                logging.debug(f"Extracted {len(text)} characters from page {i+1}")
                redacted, page_stats = redact_sensitive_info(text)
                redacted_text.append(redacted)
                redaction_stats.append(page_stats)

                # Aggregate stats
                for key, value in page_stats.items():
                    if key in total_redactions:
                        total_redactions[key] += value
                    else:
                        total_redactions[key] = value

                logging.info(f"Page {i+1} processed successfully with {sum(page_stats.values())} redactions")
            except Exception as e:
                logging.error(f"Error processing page {i+1}: {str(e)}")
                redacted_text.append(f"[Error processing this page: {str(e)}]")
                redaction_stats.append({})

        logging.info(f"PDF processing complete with {sum(total_redactions.values()) if total_redactions else 0} total redactions")
        return {
            "success": True,
            "redacted_text": redacted_text,
            "redaction_stats": redaction_stats,
            "total_redactions": total_redactions,
            "total_pages": len(redacted_text)
        }

    except Exception as e:
        logging.error(f"Error processing PDF: {str(e)}", exc_info=True)
        return {"error": f"Failed to process the PDF: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    # Use 0.0.0.0 to listen on all network interfaces
    uvicorn.run(app, host="0.0.0.0", port=8001)