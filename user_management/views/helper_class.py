from user_management import models as user_management_model


class UserValidation:
    @staticmethod
    def is_consecutive_number(num):
        count = 1
        for i in range(len(num) - 1):
            current_digit = int(num[i])
            next_digit = int(num[i + 1])

            if next_digit == current_digit + 1:
                count += 1
        if count == len(num):
            return False
        return True

    @staticmethod
    def generate_username(location, phone_number):
        last_id = 0
        try:
            last_instance = user_management_model.User.objects.latest('id')
            last_id = last_instance.id
        except:
            pass

        return "{}_{}_{}".format(location, phone_number[-4:], str(last_id))

    @staticmethod
    def password_checker(password):
        if password.isnumeric():
            if len(password) != 4:
                return "4 digits pin required"
            if UserValidation.is_consecutive_number(password):
                return password
            else:
                return "consecutive pin found"

        else:
            return "only numbers are allowed"
