from fastapi.responses import JSONResponse
from fastapi import HTTPException
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
    pattern = r'(?:Acct|A\/c|Account|A\/C|A\/C|a\/c|a\/C)[*\s]*(\w+)\s*(?:is|has been)?\s*(credited|debited|CREDITED|DEBITED)\s*(?:with)?\s*(?:INR|Rs\.?)\s*([\d,]+\.\d{2})(?:.*?(?:Team|UPI:.*?-))?\s*([\w\s]+(?:Bank|BANK|bank))'

    async def parsing_sms(self, request):
        try:
            request_data = await request.json()
            # Uncomment the line below if you need to use ParseSmsService
            # response = await ParseSmsService.parse_sms_service(request_data)

            parsed_text = await self.filtering_sms(request_data['message'])
            parsed_msg = re.search(self.pattern, request_data['message'], re.IGNORECASE)

            # Convert Match object to a serializable format
            if parsed_msg:
                parsed_msg_data = {
                    "account_number": parsed_msg.group(1),
                    "transaction_type": parsed_msg.group(2),
                    "amount": parsed_msg.group(3),
                    "bank_name": parsed_msg.group(4)
                }
            else:
                parsed_msg_data = None

            return JSONResponse(
                status_code=200,
                content={"message": "Sms parsed successfully", "data": parsed_text, "parsed_msg": parsed_msg_data},
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
