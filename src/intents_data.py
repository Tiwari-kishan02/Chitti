INTENTS = {
    "greeting": [
        "hi", "hello", "hey", "hey chitti", "hello chitti", "namaste",
        "good morning", "good evening", "hi there", "yo", "hola", "hii",
        "hello there", "hey there chitti",
    ],
    "about": [
        "who are you", "what are you", "what is your name", "what can you do",
        "help", "help me", "what do you do", "tell me about yourself",
        "how can you help me", "what are your features", "what is chitti",
        "who made you", "are you a bot", "how do you work",
    ],
    "thanks": [
        "thanks", "thank you", "thanks a lot", "thank you chitti", "thx",
        "great thanks", "ok thanks", "awesome thank you", "bye", "goodbye",
        "see you", "ok bye", "that helps thanks", "cool thanks",
        "good bye chitti",
    ],
    "check_url": [
        "is this link safe", "check this url", "can you check this website",
        "is this website a scam", "is this link phishing",
        "check this link for me", "is www.example.com safe",
        "is this site fake", "should i click this link", "verify this url",
        "is this link dangerous", "check if this site is safe",
        "scan this link", "is this url malicious", "can i trust this website",
    ],
    "check_password": [
        "is my password strong", "check my password strength",
        "how strong is my password", "check password", "rate my password",
        "is this password safe", "test my password",
        "password strength checker", "is my password good enough",
        "how secure is my password", "check this password",
        "can you check my password", "is this a strong password",
        "evaluate my password",
    ],
    "scam_message": [
        "i got a message saying i won a lottery", "is this sms a scam",
        "someone called asking for my otp", "i received a kyc update message",
        "is this message fake", "got a text that my bank account is blocked",
        "check this message for fraud", "is this email a scam",
        "i got a suspicious message", "someone asked me to share otp",
        "a message says i won a prize", "is this whatsapp message a scam",
        "i received a message to claim refund", "is this sms from bank real",
        "got a call from fake bank", "is this offer message genuine",
    ],
    "security_qa": [
        "what is phishing", "what is ransomware", "what is malware",
        "what is two factor authentication", "what is a vpn",
        "how to stay safe online", "how to create a strong password",
        "what is social engineering", "what is a firewall", "what is https",
        "what is sql injection", "how does phishing work", "explain 2fa",
        "what is a man in the middle attack", "how can i protect my account",
        "what is an otp scam", "what is a password manager",
    ],
}



INTENTS["about"].remove("who made you")
INTENTS["about"] += [
    "tum kaun ho", "aap kaun ho", "apna intro do", "introduce yourself",
    "tum kya kar sakte ho", "tell me about you", "what is your speed",
]
INTENTS["creator"] = [
    "who made you", "who created you", "who built you", "who is your creator",
    "who is your developer", "who developed chitti", "who is your owner",
    "tumhe kisne banaya", "kisne banaya tumhe", "tumhara creator kaun hai",
    "who is your maker", "who programmed you", "who designed you",
]
INTENTS["image_request"] = [
    "generate an image of a cat", "draw a picture", "create a photo of a dog",
    "make an image", "generate a logo", "make me a picture",
    "draw a cat", "create a poster image", "generate ai image",
    "can you draw", "create a picture of a mountain", "photo bana do",
    "ek image generate karo", "draw me a house",
]
INTENTS["general"] = [
    "write a python program to reverse a string", "explain photosynthesis",
    "who is the prime minister of india", "history of the indian national congress",
    "what is the capital of france", "solve this math problem",
    "write html code for a login page", "explain object oriented programming",
    "difference between list and tuple", "tell me a joke",
    "how to learn java", "notes on dbms for bsc it",
    "explain operating system", "who was mahatma gandhi",
    "what happened in 1857", "explain the indian constitution",
    "write a c program for factorial", "what is machine learning",
    "translate this sentence to hindi", "give me study tips for exams",
    "mujhe python sikhao", "bharat ki rajniti ke baare mein batao",
    "mujhe code likh ke do", "explain recursion with example",
    "who won the 2019 election", "what is the difference between sql and nosql",
    "write a javascript function to sort an array", "summarize world war 2",
]



INTENTS["greeting"] += [
    "kaise ho", "kya haal hai", "hello bhai", "hi chitti kaise ho",
    "नमस्ते", "हेलो", "हाय", "नमस्कार चिट्टी",
]
INTENTS["about"] += [
    "तुम कौन हो", "आप कौन हैं", "अपना परिचय दो", "तुम क्या कर सकते हो",
    "aap kya kar sakte ho", "tumhara naam kya hai", "tum kya ho",
    "apne baare mein batao", "आपका नाम क्या है",
]
INTENTS["creator"] += [
    "tumhe kisne banaya hai", "tumko kisne banaya", "tumhara malik kaun hai",
    "tumhe kisne create kiya", "तुम्हें किसने बनाया", "तुम्हारा निर्माता कौन है",
    "aapko kisne banaya", "tumhara developer kaun hai",
]
INTENTS["image_request"] += [
    "ek photo banao", "mere liye image banao", "tasveer banao",
    "ek picture draw karo", "billi ki photo generate karo",
    "एक तस्वीर बनाओ", "मेरे लिए इमेज बनाओ", "कुत्ते की फोटो बनाओ",
    "logo bana do", "image generate kar do",
]
INTENTS["thanks"] += [
    "shukriya", "dhanyavad", "thank you bhai", "bahut shukriya",
    "theek hai thanks", "धन्यवाद", "शुक्रिया", "अलविदा",
    "chalo bye", "phir milte hain",
]
INTENTS["check_url"] += [
    "ye link safe hai kya", "is link ko check karo", "kya ye website fake hai",
    "ye url safe hai", "kya main is link par click kar sakta hoon",
    "link check kar do", "क्या ये लिंक सुरक्षित है", "ये वेबसाइट सही है क्या",
    "इस लिंक को जाँचो", "ye site asli hai ya fake",
]
INTENTS["check_password"] += [
    "mera password strong hai kya", "password check karo",
    "mere password ki strength batao", "ye password kaisa hai",
    "पासवर्ड चेक करो", "मेरा पासवर्ड मज़बूत है क्या", "क्या ये पासवर्ड सुरक्षित है",
    "password kitna secure hai", "password ki strength check karo",
    "kya ye password theek hai",
]
INTENTS["scam_message"] += [
    "mujhe ek message aaya hai ki maine lottery jeeti", "kya ye sms scam hai",
    "kisi ne mujhse otp maanga", "mujhe kyc update ka message aaya",
    "kya ye message fake hai", "bank ne account block kar diya aisa message aaya",
    "मुझे एक संदिग्ध मैसेज आया है", "क्या ये SMS स्कैम है",
    "किसी ने मुझसे OTP माँगा", "ye message asli hai ya scam",
]
INTENTS["security_qa"] += [
    "phishing kya hota hai", "ransomware kya hai", "malware kya hai",
    "vpn kya hota hai", "online safe kaise rahe", "strong password kaise banaye",
    "firewall kya hota hai", "फ़िशिंग क्या होती है", "रैनसमवेयर क्या है", "2fa kya hai",
]
INTENTS["general"] += [
    "python mein fibonacci ka code likho", "dbms ko aasan bhasha mein samjhao",
    "bharat ke pehle pradhan mantri kaun the", "azadi ke andolan ke baare mein batao",
    "mujhe java sikhao", "ek c program likh do factorial ka",
    "bharat ka samvidhan kya hai", "इतिहास के बारे में बताओ",
    "पायथन में कोड लिखो", "भारत के प्रधानमंत्री कौन हैं",
    "mujhe exam ke liye study tips do", "machine learning kya hai",
    "1857 mein kya hua tha", "mujhe ek joke sunao", "operating system samjhao",
]