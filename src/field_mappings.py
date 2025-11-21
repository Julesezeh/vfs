"""
Field mappings for VFS forms
Maps configuration fields to actual VFS form field selectors
"""

from typing import Dict, Any


class VFSFieldMappings:
    """Mapping of applicant data to VFS form fields"""

    # Common selectors that might be used across different pages
    COMMON_SELECTORS = {
        # Login page
        'login_email': 'input[name="email"]',
        'login_email_alt': 'input[type="email"]',
        'login_email_id': 'mat-input-0',
        'login_password': 'input[name="password"]',
        'login_password_alt': 'input[type="password"]',
        'login_password_id': 'mat-input-1',
        'login_button': 'button[type="submit"]',
        'login_button_alt': 'button.mat-raised-button',

        # Appointment selection
        'appointment_center': 'select[name="centerName"]',
        'appointment_center_alt': 'mat-select[formControlName="center"]',
        'appointment_category': 'select[name="categoryName"]',
        'appointment_category_alt': 'mat-select[formControlName="category"]',
        'appointment_date': 'input[name="appointmentDate"]',
        'appointment_time': 'select[name="appointmentTime"]',
        'check_availability_button': 'button[contains(text(), "Check")]',
        'calendar_next': 'button.mat-calendar-next-button',
        'calendar_dates': 'td.mat-calendar-body-cell',
        'available_slots': 'div.available-slot',
        'time_slot': 'mat-radio-button',

        # Personal Information
        'first_name': 'input[name="firstName"]',
        'first_name_alt': 'input[formControlName="firstName"]',
        'middle_name': 'input[name="middleName"]',
        'middle_name_alt': 'input[formControlName="middleName"]',
        'last_name': 'input[name="lastName"]',
        'last_name_alt': 'input[formControlName="lastName"]',
        'date_of_birth': 'input[name="dateOfBirth"]',
        'date_of_birth_alt': 'input[formControlName="dateOfBirth"]',
        'gender': 'select[name="gender"]',
        'gender_alt': 'mat-select[formControlName="gender"]',
        'marital_status': 'select[name="maritalStatus"]',
        'marital_status_alt': 'mat-select[formControlName="maritalStatus"]',

        # Contact Information
        'email': 'input[name="email"]',
        'email_alt': 'input[formControlName="email"]',
        'phone_country_code': 'select[name="phoneCountryCode"]',
        'phone_country_code_alt': 'mat-select[formControlName="countryCode"]',
        'phone_number': 'input[name="phoneNumber"]',
        'phone_number_alt': 'input[formControlName="phoneNumber"]',
        'alternate_phone': 'input[name="alternatePhone"]',

        # Address Information
        'address_line1': 'input[name="addressLine1"]',
        'address_line1_alt': 'input[formControlName="addressLine1"]',
        'address_line2': 'input[name="addressLine2"]',
        'address_line2_alt': 'input[formControlName="addressLine2"]',
        'city': 'input[name="city"]',
        'city_alt': 'input[formControlName="city"]',
        'state': 'input[name="state"]',
        'state_alt': 'select[formControlName="state"]',
        'postal_code': 'input[name="postalCode"]',
        'postal_code_alt': 'input[formControlName="postalCode"]',
        'country': 'select[name="country"]',
        'country_alt': 'mat-select[formControlName="country"]',

        # Passport Information
        'passport_number': 'input[name="passportNumber"]',
        'passport_number_alt': 'input[formControlName="passportNumber"]',
        'passport_issue_date': 'input[name="passportIssueDate"]',
        'passport_issue_date_alt': 'input[formControlName="passportIssueDate"]',
        'passport_expiry_date': 'input[name="passportExpiryDate"]',
        'passport_expiry_date_alt': 'input[formControlName="passportExpiryDate"]',
        'passport_issue_place': 'input[name="passportIssuePlace"]',
        'passport_issue_place_alt': 'input[formControlName="passportIssuePlace"]',
        'nationality': 'select[name="nationality"]',
        'nationality_alt': 'mat-select[formControlName="nationality"]',

        # Travel Information
        'travel_purpose': 'select[name="travelPurpose"]',
        'travel_purpose_alt': 'mat-select[formControlName="purposeOfTravel"]',
        'intended_travel_date': 'input[name="intendedTravelDate"]',
        'intended_travel_date_alt': 'input[formControlName="travelDate"]',
        'intended_stay_duration': 'input[name="stayDuration"]',
        'intended_stay_duration_alt': 'input[formControlName="duration"]',

        # Employment Information
        'occupation': 'input[name="occupation"]',
        'occupation_alt': 'input[formControlName="occupation"]',
        'employer_name': 'input[name="employerName"]',
        'employer_name_alt': 'input[formControlName="employerName"]',
        'employer_address': 'input[name="employerAddress"]',
        'employer_address_alt': 'textarea[formControlName="employerAddress"]',
        'employer_phone': 'input[name="employerPhone"]',
        'employer_phone_alt': 'input[formControlName="employerPhone"]',
        'monthly_income': 'input[name="monthlyIncome"]',
        'monthly_income_alt': 'input[formControlName="income"]',

        # Portugal Contact
        'portugal_contact_name': 'input[name="contactName"]',
        'portugal_contact_name_alt': 'input[formControlName="hostName"]',
        'portugal_contact_address': 'input[name="contactAddress"]',
        'portugal_contact_address_alt': 'textarea[formControlName="hostAddress"]',
        'portugal_contact_phone': 'input[name="contactPhone"]',
        'portugal_contact_phone_alt': 'input[formControlName="hostPhone"]',

        # Buttons and Navigation
        'next_button': 'button[contains(text(), "Next")]',
        'next_button_alt': 'button.next-button',
        'submit_button': 'button[type="submit"]',
        'submit_button_alt': 'button[contains(text(), "Submit")]',
        'continue_button': 'button[contains(text(), "Continue")]',
        'confirm_button': 'button[contains(text(), "Confirm")]',
        'book_button': 'button[contains(text(), "Book")]',
        'save_button': 'button[contains(text(), "Save")]',

        # Checkboxes and Agreements
        'terms_checkbox': 'input[type="checkbox"][name="terms"]',
        'terms_checkbox_alt': 'mat-checkbox[formControlName="termsAccepted"]',
        'declaration_checkbox': 'input[type="checkbox"][name="declaration"]',
        'privacy_checkbox': 'input[type="checkbox"][name="privacy"]',

        # Messages and Alerts
        'error_message': 'div.error-message',
        'error_message_alt': 'mat-error',
        'success_message': 'div.success-message',
        'success_message_alt': 'div.mat-snack-bar-container',
        'no_slots_message': 'div[contains(text(), "No slots")]',
        'no_slots_message_alt': 'p[contains(text(), "not available")]',
    }

    # XPath selectors as fallback
    XPATH_SELECTORS = {
        'login_email': '//input[@type="email" or @name="email"]',
        'login_password': '//input[@type="password" or @name="password"]',
        'login_button': '//button[contains(text(), "Login") or contains(text(), "Sign In") or @type="submit"]',

        'appointment_slot': '//div[contains(@class, "slot") or contains(@class, "appointment")]',
        'available_date': '//td[contains(@class, "available") or not(contains(@class, "disabled"))]',
        'time_slot': '//div[contains(text(), ":") and contains(@class, "slot")]',

        'next_button': '//button[contains(text(), "Next") or contains(text(), "Continue")]',
        'submit_button': '//button[contains(text(), "Submit") or contains(text(), "Confirm")]',
        'book_button': '//button[contains(text(), "Book") or contains(text(), "Reserve")]',

        'no_slots': '//div[contains(text(), "No slot") or contains(text(), "not available") or contains(text(), "No appointment")]',
        'error': '//div[contains(@class, "error") or contains(@class, "alert-danger")]',
        'success': '//div[contains(@class, "success") or contains(@class, "alert-success")]',
    }

    @staticmethod
    def get_field_selectors(field_name: str) -> list:
        """
        Get list of possible selectors for a field

        Args:
            field_name: Name of the field

        Returns:
            List of CSS selectors to try
        """
        selectors = []

        # Add main selector
        if field_name in VFSFieldMappings.COMMON_SELECTORS:
            selectors.append(VFSFieldMappings.COMMON_SELECTORS[field_name])

        # Add alternative selector
        alt_name = f"{field_name}_alt"
        if alt_name in VFSFieldMappings.COMMON_SELECTORS:
            selectors.append(VFSFieldMappings.COMMON_SELECTORS[alt_name])

        # Add ID-based selector
        id_name = f"{field_name}_id"
        if id_name in VFSFieldMappings.COMMON_SELECTORS:
            selectors.append(f"#{VFSFieldMappings.COMMON_SELECTORS[id_name]}")

        return selectors

    @staticmethod
    def get_xpath_selector(field_name: str) -> str:
        """
        Get XPath selector for a field

        Args:
            field_name: Name of the field

        Returns:
            XPath selector string
        """
        return VFSFieldMappings.XPATH_SELECTORS.get(field_name, '')


class VisaTypeFields:
    """Field requirements for different visa types"""

    TOURIST_VISA = [
        'first_name', 'last_name', 'date_of_birth', 'gender',
        'passport_number', 'passport_expiry_date',
        'email', 'phone_number',
        'intended_travel_date', 'intended_stay_duration',
        'portugal_contact_name', 'portugal_contact_address'
    ]

    WORK_VISA = [
        'first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender', 'marital_status',
        'passport_number', 'passport_issue_date', 'passport_expiry_date', 'passport_issue_place',
        'nationality', 'email', 'phone_number',
        'address_line1', 'city', 'country',
        'occupation', 'employer_name', 'employer_address', 'employer_phone',
        'intended_travel_date', 'intended_stay_duration',
        'portugal_contact_name', 'portugal_contact_address', 'portugal_contact_phone'
    ]

    @staticmethod
    def get_required_fields(visa_type: str) -> list:
        """
        Get required fields for visa type

        Args:
            visa_type: Type of visa (tourist, work, etc.)

        Returns:
            List of required field names
        """
        visa_type = visa_type.lower()
        if visa_type == 'tourist':
            return VisaTypeFields.TOURIST_VISA
        elif visa_type == 'work':
            return VisaTypeFields.WORK_VISA
        else:
            return VisaTypeFields.TOURIST_VISA  # Default to tourist
