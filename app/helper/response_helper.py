class ResponseServiceHelper:
    def success_helper(statusCode:int, msg:dict):
        return  dict(
            status_code = statusCode,
            content = msg
        )