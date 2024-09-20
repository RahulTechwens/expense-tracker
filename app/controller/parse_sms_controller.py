from fastapi.responses import JSONResponse  # type: ignore
from fastapi import HTTPException  # type: ignore
import re
from datetime import datetime
from app.models.expense_model import Expense

class ParseSmsController:
    categories = {
        "Banking": [
            "credited",
            "debited",
            "balance",
            "account",
            "payment",
            "UPI",
            "cr",
            "dr",
        ],
        "Shopping": ["purchase", "spent", "at", "store", "mall"],
        "Utilities": ["bill", "electricity", "water", "internet", "phone"],
        "Insurance": ["insurance", "premium"],
        "Entertainment": ["movie", "tickets"],
        "Recharge": ["recharge", "mobile"],
    }

    pattern = r"([A-Za-z\s]+(?:Bank|BOB))"

    regex_for_sms_parsing = r"(?:Acct|A\/c|Account|A\/C|A\/C|a\/c|a\/C)[*\s]*(\w+)\s*(?:is|has been)?\s*(credited|debited|CREDITED|DEBITED)\s*(?:with)?\s*(?:INR|Rs\.?)\s*([\d,]+\.\d{2})(?:.*?(?:Team|UPI:.*?-))?\s*([\w\s]+(?:Bank|BANK|bank))"

    async def parsing_sms(self, request):
        try:
            request_data = await request.json()
            parsed_text = await self.filtering_sms(request_data["message"])
            parsed_bank = re.findall(
                self.pattern, request_data["message"], re.IGNORECASE
            )
            parsed_message = self.get_parsed_sms(parsed_bank, request_data["message"], parsed_text)

            return JSONResponse(
                status_code=200,
                content={
                    "message": "Sms parsed successfully",
                    "data": parsed_text,
                    "parsed_bank": parsed_bank,
                    "parsed_message": parsed_message,
                },
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def filtering_sms(message: str):
        message_lower = message.lower()
        for category, keywords in ParseSmsController.categories.items():
            if any(keyword in message_lower for keyword in keywords):
                return category
        return "Other"
    
    def generate_slug(merchant_name):
        merchant_name = merchant_name.lower()
        merchant_name = re.sub(r'[\s\-]+', '_', merchant_name)
        merchant_slug = re.sub(r'[^\w_]', '', merchant_name)
        return merchant_slug



    @staticmethod
    def get_parsed_sms(parsed_bank_name: list, message: str, parsed_text: str):
        if any(
            bank in parsed_bank_name for bank in ["Team IDFC FIRST Bank", "ICICI Bank"]
        ):
            regex_for_sms_parsing = r"(?:Acct|A\/c|Account|A\/C|A\/C|a\/c|a\/C)[*\s]*(\w+)\s*(?:is|has been)?\s*(credited|debited|CREDITED|DEBITED)\s*(?:with)?\s*(?:INR|Rs\.?)\s*([\d,]+\.\d{2})(?:.*?(?:Team|UPI:.*?-))?\s*([\w\s]+(?:Bank|BANK|bank))"
            parsed_msg = re.search(regex_for_sms_parsing, message, re.IGNORECASE)
            if parsed_msg:
                # return dict(
                #     account_number=parsed_msg.group(1),
                #     type=parsed_msg.group(2),
                #     amount=parsed_msg.group(3),
                # )
                account_number = parsed_msg.group(1)
                type=parsed_msg.group(2),
                amount=parsed_msg.group(3),
                
                expense = Expense(
                    cat=parsed_text,
                    merchant="",
                    acct="",
                    bank="",
                    date="",
                    amount=1,
                    type="",
                    method = "N/A",
                    manual= False,
                )

                expense.save()  # Await the save operation if you're in an async context
                return str(expense.id)
                
                
            else:
                return {"error": "Failed to parse SMS details"}
            
            
            
        elif any(bank in parsed_bank_name for bank in [" From HDFC Bank"]):
            regex_for_hdfc = r"Amt\s(Sent|Received)\sRs\.(\d+\.?\d*)\sFrom\s([A-Z\s]+)\sBank\sA\/C\s\*([0-9]{4})\sTo\s([A-Za-z-]+)"

            parsed_msg = re.search(regex_for_hdfc, message, re.IGNORECASE)

            if parsed_msg:
                return dict(
                    transaction_type=(
                        "credit" if parsed_msg.group(1) == "Sent" else "debit"
                    ),
                    amount=parsed_msg.group(2),
                    bank=parsed_msg.group(3),
                    account_number=parsed_msg.group(4),
                    recipient=parsed_msg.group(5),
                )
            else:
                return {"error": "Failed to parse SMS details"}
            
            
            
        elif any(bank in parsed_bank_name for bank in [" Indian Bank", "Indian Bank"]):
            regex_for_indian_bank = r"A\/c \*([0-9]{4})\s(debited|credited)\sRs\.\s([\d,]+(?:\.\d{2})?)\s+on\s(\d{2}-\d{2}-\d{2})\s+to\s([A-Za-z\-]+)\."
            regex_for_indian_bank_1 = r"Rs\.(\d+\.\d+) (credited|debited) to a\/c \*(\d+) on (\d{2}\/\d{2}\/\d{4}) by a\/c linked to VPA (\S+) \(UPI Ref no \d+\)\. Dial \d+ for Cyber Fraud -Indian Bank"

            parsed_msg = re.search(regex_for_indian_bank, message, re.IGNORECASE)
            if parsed_msg:
                return dict(
                    account_number=parsed_msg.group(1),
                    transaction_type=parsed_msg.group(2),
                    amount=parsed_msg.group(3),
                    date=parsed_msg.group(4),
                    recipient=parsed_msg.group(5),
                )

            parsed_msg = re.search(regex_for_indian_bank_1, message, re.IGNORECASE)
            if parsed_msg:
                return dict(
                    account_number=parsed_msg.group(1),
                    transaction_type=parsed_msg.group(2),
                    amount=parsed_msg.group(3),
                    date=parsed_msg.group(4),
                    recipient=parsed_msg.group(5),
                )

            return {"error": "Failed to parse SMS details"}
        elif any(bank in parsed_bank_name for bank in [" Canara Bank", "Canara Bank"]):
            regex_for_canara = {
                "transaction_type": r"(\bCREDITED\b|\bDEBITED\b)",
                "amount": r"INR\s([\d,]+\.\d{2})",
                "bank": r"\b([A-Za-z\s]+Bank)\b",
                "account_number": r"account\s(\w+)",
                "recipient": r"(?:your\saccount\s)(\w+)",
            }
            extracted_info = {}
            for key, pattern in regex_for_canara.items():
                match = re.search(pattern, message)
                if match:
                    extracted_info[key] = match.group(1).strip()

            # if parsed_msg:
            return extracted_info
        
        
        
        
        
        
        
        
        elif any(bank in parsed_bank_name for bank in [" Axis Bank", "Axis Bank"]):
            regex_for_axis = {
                "transaction_type": r"(credited|debited)",
                "amount": r"INR\s([\d,]+\.\d{2})",
                "account_number": r"A/c\sno\.\s([Xx*\d]+)",
                "bank": r"-\s([A-Za-z\s]+)\sBank",
                "recipient": r"Info-\s(?:UPI|P2A|IMPS)/[\d]+/([A-Za-z\s]+)",
                "date_time": r"on\s(\d{2}-\d{2}-\d{2,4})\sat\s([\d:]+)",
            }
            extracted_info = {}
            for key, pattern in regex_for_axis.items():
                match = re.search(pattern, message)
                if match:
                    extracted_info[key] = match.group(1).strip()
                    
                    
            expense = Expense(
                cat=parsed_text,
                merchant=extracted_info.get("recipient", "N/A"),
                acct=extracted_info["account_number"],
                bank=extracted_info["bank"],
                date=extracted_info["date_time"],
                amount=float(extracted_info["amount"]),
                type=extracted_info["transaction_type"],
                method = "N/A",
                manual= False,
            )
            
            

            expense.save()  # Await the save operation if you're in an async context
            return str(expense.id)

            # if parsed_msg:
            # return extracted_info







        elif any(
            bank in parsed_bank_name for bank in [" Bank of Baroda ", " Bank of Baroda "]
        ):
            regex_for_axis = {
                "transaction_type": r"(Credited|Debited)",
                "amount": r"Rs\.(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
                "account_number": r"A/c\s\.\.\.\d{4}",
                "bank": r"-\s([A-Za-z\s]+)$",
                "recipient": r"by\s([a-zA-Z0-9._]+)",
                "date_time": r"\((\d{2}-\d{2}-\d{4})\s(\d{2}:\d{2}:\d{2})\)",
            }
            extracted_info = {}
            for key, pattern in regex_for_axis.items():
                match = re.search(pattern, message)
                if match:
                    extracted_info[key] = match.group(1).strip()

            # if parsed_msg:
            return extracted_info

        return None
