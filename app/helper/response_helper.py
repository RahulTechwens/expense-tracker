class ResponseServiceHelper:
    def success_helper(msg:dict, statusCode:int):
        return  dict(
            status_code = statusCode,
            content = msg
        )