from fastapi.responses import JSONResponse # type: ignore
from fastapi import HTTPException # type: ignore
import re

class ParseSmsController:
    categories = {
        'Banking': ['credited', 'debited', 'balance', 'account', 'payment', 'UPI', 'cr', 'dr'],
        'Shopping': ['purchase', 'spent', 'at', 'store', 'mall'],
        'Utilities': ['bill', 'electricity', 'water', 'internet', 'phone'],
        'Insurance': ['insurance', 'premium'],
        'Entertainment': ['movie', 'tickets'],
        'Recharge': ['recharge', 'mobile']
    }

    pattern = r"([A-Za-z\s]+(?:Bank|BOB))"
    
    regex_for_sms_parsing = r'(?:Acct|A\/c|Account|A\/C|A\/C|a\/c|a\/C)[*\s]*(\w+)\s*(?:is|has been)?\s*(credited|debited|CREDITED|DEBITED)\s*(?:with)?\s*(?:INR|Rs\.?)\s*([\d,]+\.\d{2})(?:.*?(?:Team|UPI:.*?-))?\s*([\w\s]+(?:Bank|BANK|bank))'

    async def parsing_sms(self, request):
        try:
            request_data = await request.json()
            parsed_text = await self.filtering_sms(request_data['message'])
            parsed_bank = re.findall(self.pattern, request_data['message'], re.IGNORECASE)
            parsed_message = self.get_parsed_sms(parsed_bank, request_data['message'])

            return JSONResponse(
                status_code=200,
                content={
                    "message": "Sms parsed successfully", 
                    "data": parsed_text, 
                    "parsed_bank": parsed_bank,
                    "parsed_message": parsed_message
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
        return 'Other'

    @staticmethod
    def get_parsed_sms(parsed_bank_name: list, message: str):
        if any(bank in parsed_bank_name for bank in ['Team IDFC FIRST Bank', 'ICICI Bank']):
            regex_for_sms_parsing = r'(?:Acct|A\/c|Account|A\/C|A\/C|a\/c|a\/C)[*\s]*(\w+)\s*(?:is|has been)?\s*(credited|debited|CREDITED|DEBITED)\s*(?:with)?\s*(?:INR|Rs\.?)\s*([\d,]+\.\d{2})(?:.*?(?:Team|UPI:.*?-))?\s*([\w\s]+(?:Bank|BANK|bank))'
            
            parsed_msg = re.search(regex_for_sms_parsing, message, re.IGNORECASE)
            
            if parsed_msg:
                return dict(
                    account_number=parsed_msg.group(1),
                    type=parsed_msg.group(2),
                    amount=parsed_msg.group(3)
                )
            else:
                return {"error": "Failed to parse SMS details"}
        elif any(bank in parsed_bank_name for bank in [' From HDFC Bank']):
            regex_for_hdfc = r"Amt\s(Sent|Received)\sRs\.(\d+\.?\d*)\sFrom\s([A-Z\s]+)\sBank\sA\/C\s\*([0-9]{4})\sTo\s([A-Za-z-]+)"
            
            parsed_msg = re.search(regex_for_hdfc, message, re.IGNORECASE)
            
            if parsed_msg:
                return dict(
                    transaction_type = "credit" if parsed_msg.group(1)== "Sent" else "debit",
                    amount = parsed_msg.group(2),     
                    bank = parsed_msg.group(3),        
                    account_number = parsed_msg.group(4),
                    recipient = parsed_msg.group(5)
                )
            else:
                return {"error": "Failed to parse SMS details"}
        elif any(bank in parsed_bank_name for bank in [' Indian Bank', 'Indian Bank']):
            regex_for_indian_bank = r"A\/c \*([0-9]{4})\s(debited|credited)\sRs\.\s([\d,]+(?:\.\d{2})?)\s+on\s(\d{2}-\d{2}-\d{2})\s+to\s([A-Za-z\-]+)\."
            regex_for_indian_bank_1 = r"Rs\.(\d+\.\d+) (credited|debited) to a\/c \*(\d+) on (\d{2}\/\d{2}\/\d{4}) by a\/c linked to VPA (\S+) \(UPI Ref no \d+\)\. Dial \d+ for Cyber Fraud -Indian Bank"

            parsed_msg = re.search(regex_for_indian_bank, message, re.IGNORECASE)
            if parsed_msg:
                return dict(
                    account_number=parsed_msg.group(1),
                    transaction_type=parsed_msg.group(2),
                    amount=parsed_msg.group(3),
                    date=parsed_msg.group(4),
                    recipient=parsed_msg.group(5)
                )
            
            parsed_msg = re.search(regex_for_indian_bank_1, message, re.IGNORECASE)
            if parsed_msg:
                return dict(
                    account_number=parsed_msg.group(1),
                    transaction_type=parsed_msg.group(2),
                    amount=parsed_msg.group(3),
                    date=parsed_msg.group(4),
                    recipient=parsed_msg.group(5)
                )
            
            return {"error": "Failed to parse SMS details"}
        elif any(bank in parsed_bank_name for bank in [' Canara Bank', 'Canara Bank']):
            regex_for_canara = {
                'transaction_type': r'(\bCREDITED\b|\bDEBITED\b)',
                'amount': r'INR\s([\d,]+\.\d{2})',
                'bank': r'\b([A-Za-z\s]+Bank)\b',
                'account_number': r'account\s(\w+)',
                'recipient': r'(?:your\saccount\s)(\w+)'
            }
            extracted_info = {}
            for key, pattern in regex_for_canara.items():
                match = re.search(pattern, message)
                if match:
                    extracted_info[key] = match.group(1).strip()
                        
            # if parsed_msg:
            return extracted_info
        return None
