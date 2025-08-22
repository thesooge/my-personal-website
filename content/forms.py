"""Forms for the content app."""

from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """Contact form with honeypot field."""
    
    # Honeypot field to catch bots
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput,
        label="",
        help_text=""
    )
    
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "placeholder": "Your name",
                    "aria-label": "Your name"
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "placeholder": "your.email@example.com",
                    "aria-label": "Your email address"
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "rows": 5,
                    "placeholder": "Your message...",
                    "aria-label": "Your message"
                }
            ),
        }
        labels = {
            "name": "Name",
            "email": "Email",
            "message": "Message",
        }
        help_texts = {
            "name": "Please enter your full name.",
            "email": "We'll use this to get back to you.",
            "message": "Tell us what you'd like to discuss.",
        }
    
    def clean_website(self):
        """Check honeypot field."""
        website = self.cleaned_data.get("website")
        if website:
            raise forms.ValidationError("Form submission failed.")
        return website
    
    def clean_name(self):
        """Validate name field."""
        name = self.cleaned_data.get("name")
        if not name or len(name.strip()) < 2:
            raise forms.ValidationError("Please enter a valid name (at least 2 characters).")
        return name.strip()
    
    def clean_message(self):
        """Validate message field."""
        message = self.cleaned_data.get("message")
        if not message or len(message.strip()) < 10:
            raise forms.ValidationError("Please enter a message (at least 10 characters).")
        return message.strip() 