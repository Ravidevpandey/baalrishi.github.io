"""Build both static language pages. Run: python3 scripts/build.py"""
from pathlib import Path
from html import escape as e
import json
ROOT = Path(__file__).resolve().parent.parent
config = json.loads((ROOT / 'site-config.json').read_text())
services = [
('kundali','01','◇','₹751',
 ['जन्म कुंडली विश्लेषण','Birth chart consultation'],
 ['अपने जन्म विवरण को पारंपरिक ज्योतिष के नज़रिए से समझें। जीवन के विषयों और अपने सवालों पर एक केंद्रित बातचीत।','Explore your birth details through traditional astrology, with a focused conversation about your life themes and questions.'],
 ['जन्म तिथि, यथासंभव सही जन्म समय, जन्म स्थान और आपके मुख्य सवाल। समय पता न हो तो पहले बताएं।','Your birth date, time as accurately as known, birthplace and main questions. Let us know if your birth time is uncertain.'],
 ['ग्रहों और भावों का पारंपरिक अध्ययन, आपके चुने हुए विषयों की चर्चा और इच्छानुसार सामान्य आध्यात्मिक अभ्यास की जानकारी।','A traditional reading of planets and houses, discussion of your chosen topics, and optional information about general spiritual practices.'],
 ['जन्म विवरण की पुष्टि के बाद कुंडली पर चर्चा की जाती है। परामर्श का माध्यम, समय और दायरा बुकिंग से पहले तय करें।','After confirming your birth details, the chart is discussed with you. Confirm the consultation format, timing and scope before booking.'],
 [['अपनी कुंडली और जीवन के प्रमुख विषयों की स्पष्ट, व्यवस्थित समझ','अपने सवालों पर केंद्रित, व्यक्तिगत बातचीत','निर्णय लेने से पहले एक पारंपरिक दृष्टिकोण से सोचने का मौका','मन की उलझन को शब्दों में रखकर हल्का महसूस करना'],
  ['A clear, organised understanding of your birth chart and key life themes','A focused, one-on-one conversation about your specific questions','A traditional perspective to consider before you decide','A calmer mind after putting your concerns into words']]),
('marriage','02','∞','₹551 – ₹851',
 ['विवाह मार्गदर्शन','Marriage guidance'],
 ['विवाह और साझेदारी से जुड़े प्रश्नों पर पारंपरिक कुंडली दृष्टिकोण। निर्णय में आपकी इच्छा और आपसी सहमति सबसे महत्वपूर्ण हैं।','A traditional birth-chart perspective on marriage and partnership, with personal choice and mutual consent at the centre.'],
 ['अपने जन्म विवरण और सवाल; दूसरे व्यक्ति की जानकारी केवल उनकी सहमति से साझा करें।','Your birth details and questions. Share another person’s details only with their consent.'],
 ['विवाह से जुड़े पारंपरिक संकेतों की चर्चा, अपेक्षाओं पर बातचीत और साथ में विचार करने योग्य विषय।','Discussion of traditional marriage indicators, expectations and topics to reflect on together.'],
 ['पहले प्रश्न और उपलब्ध विवरण समझे जाते हैं, फिर परामर्श का दायरा तय होता है। किसी विवाह, तिथि या रिश्ते के परिणाम की गारंटी नहीं है।','We first understand your questions and available details, then agree on the scope. No marriage, date or relationship outcome is guaranteed.'],
 [['विवाह से जुड़े संकेतों और समय पर पारंपरिक स्पष्टता','अपेक्षाओं और चिंताओं पर खुलकर बात करने का सुरक्षित स्थान','परिवार या साथी से बातचीत के लिए बेहतर तैयारी','अपने निर्णय पर भरोसा बढ़ाने वाली सोच-समझ'],
  ['Traditional clarity on marriage-related timing and indicators','A safe space to voice expectations and concerns openly','Better preparation for conversations with family or a partner','Greater confidence in your own decision-making']]),
('love','03','♡','₹551 – ₹851',
 ['प्रेम एवं संबंध','Love & relationships'],
 ['रिश्तों की उलझनों पर संवेदनशील बातचीत और आत्मचिंतन के लिए पारंपरिक आध्यात्मिक दृष्टिकोण।','A thoughtful conversation about relationship concerns and a traditional spiritual perspective for personal reflection.'],
 ['अपना प्रश्न और आवश्यक पृष्ठभूमि। निजी चैट या किसी अन्य की संवेदनशील जानकारी भेजने की आवश्यकता नहीं है।','Your question and relevant background. You do not need to send private chats or sensitive information about someone else.'],
 ['रिश्ते से जुड़ी चिंताओं की चर्चा, आपकी अपेक्षाओं पर आत्मचिंतन और वैकल्पिक साधना की सामान्य जानकारी।','Discussion of your concerns, reflection on your expectations and general information about optional spiritual practices.'],
 ['आपकी बात सुनकर उपलब्ध जानकारी के आधार पर चर्चा होती है। किसी को नियंत्रित करने, वशीकरण या प्रेम वापस लाने का दावा नहीं किया जाता।','We listen to your concerns and discuss the information available. We do not offer control over another person or promise to bring someone back.'],
 [['रिश्ते की उलझन को बिना जजमेंट के समझने का मौका','अपनी भावनाओं और अपेक्षाओं को स्पष्ट करने में मदद','आत्मचिंतन के लिए एक पारंपरिक आध्यात्मिक नज़रिया','अगला कदम खुद तय करने का आत्मविश्वास'],
  ['A non-judgmental space to understand your relationship concerns','Help clarifying your own feelings and expectations','A traditional spiritual perspective for self-reflection','Confidence to decide your own next step']]),
('santan','04','⌂','₹751 – ₹1,100',
 ['संतान एवं परिवार','Children & family'],
 ['परिवार से जुड़े प्रश्नों पर आस्था-आधारित मार्गदर्शन और शांतिपूर्ण आत्मचिंतन के लिए स्थान।','Faith-based guidance and space for reflection on questions about family life.'],
 ['अपने प्रश्न और केवल आवश्यक जन्म विवरण। चिकित्सा रिपोर्ट भेजने की आवश्यकता नहीं है।','Your questions and only the birth details needed for the discussion. Medical reports are not required.'],
 ['पारिवारिक विषयों पर पारंपरिक ज्योतिषीय चर्चा और इच्छानुसार प्रार्थना या ध्यान की सामान्य जानकारी।','Traditional astrological discussion of family themes and optional general information about prayer or meditation.'],
 ['पहले आपकी अपेक्षाएं और सेवा की सीमाएं स्पष्ट की जाती हैं। यह प्रजनन उपचार नहीं है; गर्भधारण, संतान या शिशु के लिंग की भविष्यवाणी या गारंटी नहीं दी जाती।','We first clarify expectations and the limits of the service. This is not fertility treatment; we do not predict or guarantee conception, children or a baby’s sex.'],
 [['पारिवारिक विषयों पर पारंपरिक दृष्टिकोण और मानसिक शांति','अपेक्षाओं और सीमाओं की शुरुआत में ही स्पष्टता','चिंता के समय भावनात्मक सहारा और सुनने वाला कोई','इच्छानुसार प्रार्थना या ध्यान जैसे सरल अभ्यासों की जानकारी'],
  ['A traditional perspective and peace of mind around family questions','Clarity on expectations and limits right from the start','Emotional support and a listening ear during an anxious time','Optional guidance on simple practices like prayer or meditation']]),
('mantra','05','✺','₹251 – ₹1,100',
 ['मंत्र साधना एवं ध्यान','Mantra & meditation'],
 ['दैनिक जीवन में एक सरल आध्यात्मिक अभ्यास के लिए पारंपरिक मंत्र, जप और ध्यान का परिचय।','An introduction to traditional mantra, chanting and meditation for a simple spiritual practice in everyday life.'],
 ['आपकी रुचि, परंपरा और अभ्यास के लिए उपलब्ध समय। किसी विशेष धार्मिक मान्यता को अपनाना आवश्यक नहीं है।','Your interests, tradition and the time you can set aside. You are not required to adopt a particular religious belief.'],
 ['अभ्यास की सामान्य प्रक्रिया, सहज दिनचर्या बनाने पर चर्चा और अपने सहज स्तर पर अभ्यास का मार्गदर्शन।','An introduction to the practice, discussion of a manageable routine and guidance on practising at your own comfort level.'],
 ['आपके अनुभव के अनुसार शुरुआती अभ्यास पर चर्चा होती है। भागीदारी स्वैच्छिक है; चमत्कार, रोगमुक्ति या निश्चित परिणाम का दावा नहीं है।','We discuss an introductory practice suited to your experience. Participation is voluntary; no miracle, cure or specific result is promised.'],
 [['रोज़ के जीवन में शामिल करने योग्य सरल आध्यात्मिक अभ्यास','अपनी गति से सीखने का सहज, दबाव-मुक्त तरीका','मानसिक शांति और नियमित दिनचर्या बनाने में सहायता','परंपरा से जुड़ाव महसूस करने का अवसर'],
  ['A simple spiritual practice you can build into daily life','An easy, pressure-free way to learn at your own pace','Support in building a calming, regular routine','A chance to feel connected to tradition']])]
texts = {
'nav':[['सेवाएँ','प्रक्रिया','हमारे बारे में','संपर्क'],['Services','How it works','About','Contact']],
'brand':['पारंपरिक ज्ञान • सहज मार्गदर्शन','Traditional wisdom • Thoughtful guidance'],
'eyebrow':['आस्था, समझ और आत्मचिंतन','FAITH. REFLECTION. PERSPECTIVE.'],
'hero':['परंपरा से जुड़ें।<br><em>खुद को समझें।</em>','Rooted in tradition.<br><em>Space to reflect.</em>'],
'desc':['जीवन के सवालों पर एक ठहराव, एक बातचीत और एक नया दृष्टिकोण। बाल ऋषि के साथ पारंपरिक ज्योतिष एवं आध्यात्मिक परामर्श।','A moment to pause. A conversation about what matters. Explore traditional astrology and spiritual guidance with Baal Rishi.'],
'book':['परामर्श के लिए संपर्क करें','Enquire about a consultation'],
'explore':['हमारी सेवाएँ देखें ↗','Explore our services ↗'],
'heroNote':['आस्था-आधारित मार्गदर्शन · परिणाम की गारंटी नहीं','Faith-based guidance · No guaranteed outcomes'],
'serviceTag':['आपकी जिज्ञासा, हमारा संवाद','A CONVERSATION THAT STARTS WITH YOU'],
'servicesTitle':['आपके लिए परामर्श','Find your consultation'],
'servicesIntro':['हर सेवा में क्या शामिल है, क्या जानकारी चाहिए और प्रक्रिया कैसी होगी—बुकिंग से पहले विस्तार से जानें।','Understand what each service includes, what to prepare and how it works before you book.'],
'details':['विवरण और प्रक्रिया','Details & process'],
'benefitsHeading':['इससे आपको क्या मिलता है','What you gain'],
'prepare':['क्या जानकारी चाहिए','What to prepare'],
'include':['क्या शामिल है','What is included'],
'process':['कैसे होगा','How it works'],
'feeNote':['सूचीबद्ध शुल्क। अंतिम शुल्क और दायरा बुकिंग से पहले तय करें।','Listed fee. Confirm the final fee and scope before booking.'],
'choose':['इस सेवा के बारे में पूछें ↗','Enquire about this service ↗'],
'commonShort':['सभी सेवाओं पर नीचे दी गई महत्वपूर्ण सूचना लागू है।','The important notice below applies to every service.'],
'noticeLink':['महत्वपूर्ण सूचना पढ़ें','Read the important notice'],
'howTag':['सरल और स्पष्ट','SIMPLE & CONSIDERED'],
'howTitle':['परामर्श तक, तीन आसान कदम','Your consultation, in three steps'],
'steps':[[('सेवा चुनें','विवरण पढ़ें और वह सेवा चुनें जो आपके प्रश्न से संबंधित हो।'),('पहले बात करें','फॉर्म या Instagram से संपर्क करें। शुल्क, माध्यम, उपलब्ध समय और रद्द करने की शर्तें पहले तय करें।'),('फिर परामर्श लें','पुष्टि के बाद ही भुगतान करें और तय माध्यम पर परामर्श में शामिल हों।')],[('Explore a service','Read the details and choose the service that relates to your question.'),('Confirm the details','Contact us by form or Instagram. Agree on the fee, format, availability and cancellation terms first.'),('Join your consultation','Pay only after confirmation and join through the agreed consultation format.')]],
'aboutTag':['बाल ऋषि के बारे में','ABOUT BAAL RISHI'],
'aboutTitle':['परंपरा का सम्मान।<br>आपकी समझ को महत्व।','Respect for tradition.<br>Room for your own judgment.'],
'aboutText':['बाल ऋषि पारंपरिक ज्योतिष, कुंडली अध्ययन और आध्यात्मिक अभ्यास से जुड़े विषयों पर परामर्श का स्थान है। हमारा उद्देश्य आपकी जिज्ञासाओं पर संवाद और आत्मचिंतन में सहायता करना है।','Baal Rishi is a space for consultation on traditional astrology, birth-chart interpretation and spiritual practice. Our purpose is to support conversation and personal reflection around your questions.'],
'aboutText2':['आपके निर्णय आपके हैं। किसी भी अभ्यास में भाग लेना स्वैच्छिक है। हम भय, चमत्कार या निश्चित भविष्य के वादे के आधार पर सेवा नहीं देते।','Your decisions remain your own. Every practice is voluntary. Our services are not based on fear, miracles or promises of a certain future.'],
'illustration':['बाल ऋषि का चित्र','Baal Rishi portrait'],
'paymentTag':['पुष्टि के बाद भुगतान','PAYMENT AFTER CONFIRMATION'],
'paymentTitle':['पहले जानकारी। फिर भुगतान।','Clarity first. Payment second.'],
'paymentText':['सेवा, अंतिम शुल्क, परामर्श का समय, माध्यम और रद्द करने या रिफंड की शर्तें पहले संपर्क करके समझ लें। भुगतान मात्र से बुकिंग की पुष्टि नहीं होती।','Contact us first to confirm the service, final fee, consultation time, format and cancellation or refund terms. Payment alone does not confirm a booking.'],
'paymentNote':['QR में दिखने वाले प्राप्तकर्ता की पुष्टि करें। OTP, UPI PIN या बैंक पासवर्ड कभी साझा न करें।','Verify the recipient shown by your payment app. Never share an OTP, UPI PIN or banking password.'],
'qr':['भुगतान QR खोलें ↗','Open payment QR ↗'],
'contactTag':['बातचीत की शुरुआत','LET’S START A CONVERSATION'],
'contactTitle':['आप क्या समझना चाहते हैं?','What would you like to explore?'],
'contactText':['सेवा और अपने मुख्य प्रश्न के साथ संपर्क करें। उपलब्ध समय और परामर्श के माध्यम की पुष्टि बातचीत में की जाएगी।','Get in touch with your chosen service and main question. Availability and the consultation format will be confirmed with you.'],
'formTitle':['परामर्श फॉर्म','Consultation form'],
'formAvailable':['अपनी सेवा और संपर्क विवरण सुरक्षित रूप से Google Form में भरें। फॉर्म नए टैब में खुलेगा।','Share your chosen service and contact details through Google Forms. The form opens in a new tab.'],
'formUnavailable':['ऑनलाइन फॉर्म अभी उपलब्ध नहीं है। फिलहाल Instagram पर संदेश भेजकर परामर्श की जानकारी लें।','The online form is not available yet. Please message us on Instagram to enquire about a consultation.'],
'formButton':['Google Form खोलें ↗','Open Google Form ↗'],
'instaText':['सेवा, समय और शुल्क की जानकारी के लिए संदेश भेजें। जवाब में बुकिंग के अगले कदम तय करें।','Message us about the service, availability and fee, then agree on the next steps for booking.'],
'instaButton':['Instagram पर संपर्क करें ↗','Contact on Instagram ↗'],
'privacy':['केवल आवश्यक जानकारी साझा करें। सार्वजनिक टिप्पणी में जन्म विवरण, भुगतान विवरण या निजी समस्याएं न लिखें। Google Forms और Instagram पर उनकी अपनी गोपनीयता नीतियां लागू होती हैं।','Share only the information needed. Do not post birth details, payment information or personal concerns in public comments. Google Forms and Instagram apply their own privacy policies.'],
'faqTitle':['आपके कुछ सवाल','A few common questions'],
'faqs':[[('क्या किसी परिणाम की गारंटी है?','नहीं। यह पारंपरिक और आस्था-आधारित मार्गदर्शन है। निश्चित भविष्य, विवाह, सफलता, संतान, रोगमुक्ति या किसी अन्य परिणाम की गारंटी नहीं दी जाती।'),('परामर्श कब और किस माध्यम से होगा?','उपलब्ध समय, माध्यम, अवधि और भाषा संपर्क के बाद तय होंगे। वेबसाइट का अनुवाद होना उस भाषा में परामर्श उपलब्ध होने की पुष्टि नहीं है।'),('जन्म का सही समय पता न हो तो?','बुकिंग से पहले बता दें। उपलब्ध जानकारी के आधार पर सेवा उपयुक्त है या नहीं और उसकी सीमाएं क्या होंगी, यह पहले स्पष्ट करें।'),('भुगतान और रिफंड के बारे में कैसे जानें?','भुगतान से पहले अंतिम शुल्क और रद्द करने, पुनर्निर्धारण तथा रिफंड की शर्तें लिखित रूप में पूछ लें। वेबसाइट पर तत्काल बुकिंग की सुविधा नहीं है।')],[('Are any outcomes guaranteed?','No. This is traditional, faith-based guidance. We do not guarantee a certain future, marriage, success, children, healing or any other outcome.'),('When and how will the consultation happen?','Availability, format, duration and consultation language are agreed after you contact us. A translated website does not confirm that consultations are available in that language.'),('What if I do not know my birth time?','Tell us before booking. First clarify whether the service is suitable with the available information and what its limitations will be.'),('What about payment and refunds?','Ask for the final fee and the cancellation, rescheduling and refund terms in writing before paying. This website does not offer instant booking.')]],
'noticeTitle':['महत्वपूर्ण सूचना — सभी सेवाओं के लिए','Important notice — applies to every service'],
'notice':['यहां दी गई सेवाएं पारंपरिक मान्यताओं, ज्योतिष और आध्यात्मिक अभ्यास पर आधारित हैं; इन्हें वैज्ञानिक रूप से प्रमाणित भविष्यवाणी न मानें। हम किसी घटना, निश्चित भविष्य, सफलता, विवाह, संतान, रोगमुक्ति, चमत्कार या अन्य परिणाम का दावा या गारंटी नहीं देते। यह चिकित्सा, मानसिक स्वास्थ्य उपचार, कानूनी या वित्तीय सलाह का विकल्प नहीं है। इन विषयों के लिए योग्य पेशेवर से संपर्क करें; निर्धारित उपचार न रोकें। व्यक्तिगत निर्णय अपने विवेक से लें।','These services are based on traditional beliefs, astrology and spiritual practices; they should not be treated as scientifically established predictions. We do not claim or guarantee any event, certain future, success, marriage, children, cure, miracle or other outcome. This is not a substitute for medical care, mental health treatment, legal advice or financial advice. Consult qualified professionals for those matters and do not stop prescribed treatment. Use your own judgment when making decisions.'],
'langTitle':['अपनी भाषा में पढ़ें','Read in your language'],
'langText':['हिन्दी और English सीधे उपलब्ध हैं। नीचे दी गई सूची से अपनी भाषा चुनें—पूरा पेज उसी भाषा में तुरंत बदल जाएगा (Google द्वारा स्वचालित अनुवाद)। इसमें त्रुटियां हो सकती हैं; शुल्क और सेवा की जानकारी की पुष्टि हमसे करें।','Hindi and English are available directly. Choose your language from the dropdown below and the whole page switches instantly (automatic translation by Google). It may contain errors; confirm fees and service details with us.'],
'skip':['सीधे सामग्री पर जाएँ','Skip to content'],
'footer':['आस्था के साथ, विवेक भी।','A place for faith. A space for reflection.']
}
BASE='https://ravidevpandey.github.io/baalrishi.github.io/'
from urllib.parse import urlparse
form=config.get('googleFormUrl','').strip()
if form:
 u=urlparse(form)
 if u.scheme!='https' or u.hostname not in ('docs.google.com','forms.gle') or (u.hostname=='docs.google.com' and (not u.path.startswith('/forms/') or '/edit' in u.path)): raise ValueError('Use a public HTTPS Google Forms responder link')
INCLUDED_LANGS='hi,en,bn,bho,mr,gu,ta,te,kn,ml,pa,ur,ar,ne,fr,es,de,pt,ja,zh-CN'
PLUS_ICON='<svg class="plus-icon" viewBox="0 0 20 20" aria-hidden="true"><line x1="10" y1="3" x2="10" y2="17"/><line x1="3" y1="10" x2="17" y2="10"/></svg>'
for lang,n in [('hi',0),('en',1)]:
 def t(key): return texts[key][n]
 cards=''
 for id,num,icon,price,title,desc,prep,inc,proc,benefits in services:
  benefit_items=''.join(f'<li>{b}</li>' for b in benefits[n])
  cards+=f'''<article class="service-card" id="{id}"><div class="card-top"><span class="service-symbol" aria-hidden="true">{icon}</span><span class="serial">{num}</span></div><h3>{title[n]}</h3><p>{desc[n]}</p><div class="fee">{price}</div><p class="fee-note">{t('feeNote')}</p><details><summary>{t('details')}<span aria-hidden="true">{PLUS_ICON}</span></summary><div class="service-detail"><h4>{t('benefitsHeading')}</h4><ul class="benefit-list">{benefit_items}</ul><h4>{t('prepare')}</h4><p>{prep[n]}</p><h4>{t('include')}</h4><p>{inc[n]}</p><h4>{t('process')}</h4><p>{proc[n]}</p><p class="small-note">{t('commonShort')} <a href="#notice">{t('noticeLink')}</a></p><a class="text-link" href="#contact">{t('choose')}</a></div></details></article>'''
 steps=''.join(f'<article><span class="step-num">0{i+1}</span><h3>{a}</h3><p>{b}</p></article>' for i,(a,b) in enumerate(t('steps')))
 faqs=''.join(f'<details><summary>{q}<span aria-hidden="true">{PLUS_ICON}</span></summary><p>{a}</p></details>' for q,a in t('faqs'))
 nav=''.join(f'<a href="#{id}">{label}</a>' for id,label in zip(['services','how','about','contact'],t('nav')))
 formcta=f'<a class="button primary" href="{e(form)}" target="_blank" rel="noopener noreferrer">{t("formButton")}</a>' if form else f'<a class="button outline" href="{config["instagramUrl"]}" target="_blank" rel="noopener noreferrer">{t("instaButton")}</a>'
 html=f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#183d35"><title>{'बाल ऋषि | पारंपरिक ज्योतिष एवं आध्यात्मिक परामर्श' if n==0 else 'Baal Rishi | Traditional Astrology & Spiritual Guidance'}</title><meta name="description" content="{e(t('desc'))}"><link rel="canonical" href="{BASE+('' if n==0 else 'en.html')}"><link rel="alternate" hreflang="hi" href="{BASE}"><link rel="alternate" hreflang="en" href="{BASE}en.html"><meta property="og:title" content="Baal Rishi | बाल ऋषि"><meta property="og:description" content="{e(t('desc'))}"><meta property="og:type" content="website"><meta property="og:image" content="{BASE}assets/spiritual-still-life.webp"><meta property="og:url" content="{BASE+('' if n==0 else 'en.html')}"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="style.css"><script src="app.js" defer></script></head>
<body><a class="skip-link" href="#main">{t('skip')}</a><header class="site-header"><div class="container header-inner"><a href="#home" class="brand" aria-label="Baal Rishi"><span class="brand-mark" aria-hidden="true">✺</span><span><strong>{'बाल ऋषि' if n==0 else 'Baal Rishi'}</strong><small>{t('brand')}</small></span></a><nav aria-label="{'मुख्य नेविगेशन' if n==0 else 'Main navigation'}">{nav}</nav><a class="language-link" href="#languages">◎ <span>हिन्दी / EN</span></a></div></header>
<main id="main"><section class="hero container" id="home"><div class="hero-copy"><p class="eyebrow">{t('eyebrow')}</p><h1>{t('hero')}</h1><p class="hero-description">{t('desc')}</p><div class="hero-actions"><a class="button primary" href="#contact">{t('book')} <span aria-hidden="true">↗</span></a><a class="text-link" href="#services">{t('explore')}</a></div><p class="hero-note"><span aria-hidden="true">✧</span> {t('heroNote')}</p></div><div class="hero-art"><img src="assets/hero-illustration.svg" width="1536" height="1024" fetchpriority="high" alt="{'दीपक, रुद्राक्ष और पारंपरिक कुंडली की प्रतीकात्मक सज्जा' if n==0 else 'A symbolic arrangement of a diya, prayer beads and a traditional birth chart'}"><div class="image-caption"><span aria-hidden="true">✺</span><div><strong>{'ज्ञान · आस्था · चिंतन' if n==0 else 'Wisdom · Faith · Reflection'}</strong><small>BAAL RISHI</small></div></div></div></section>
<div class="values-strip"><div class="container"><span>✧ {'पारंपरिक दृष्टिकोण' if n==0 else 'Traditional perspectives'}</span><span>✧ {'स्पष्ट सेवा विवरण' if n==0 else 'Clear service details'}</span><span>✧ {'आपका निर्णय, आपकी स्वतंत्रता' if n==0 else 'Your choice, your agency'}</span></div></div>
<section class="section container" id="services"><div class="section-heading"><p class="eyebrow">{t('serviceTag')}</p><h2>{t('servicesTitle')}</h2><p>{t('servicesIntro')}</p></div><div class="service-grid">{cards}<aside class="service-aside"><span aria-hidden="true">✺</span><h3>{'एक सवाल से<br>शुरुआत करें।' if n==0 else 'Start with<br>one question.'}</h3><p>{'सेवा चुनने में उलझन है? पहले बात करके समझें कि कौन-सा परामर्श आपके लिए उपयुक्त है।' if n==0 else 'Not sure which service to choose? Get in touch to understand which consultation fits your question.'}</p><a href="#contact" class="button light">{t('book')} ↗</a></aside></div><a class="section-notice" href="#notice">ⓘ {t('commonShort')} <span>{t('noticeLink')} ↗</span></a></section>
<section class="how-section" id="how"><div class="container section"><div class="section-heading"><p class="eyebrow">{t('howTag')}</p><h2>{t('howTitle')}</h2></div><div class="steps">{steps}</div></div></section>
<section class="section container about" id="about"><figure><a href="{e(config['instagramUrl'])}" target="_blank" rel="noopener noreferrer" aria-label="{t('instaButton')}"><img src="assets/baalrishi-portrait.png" width="768" height="1203" loading="lazy" alt="{t('illustration')}"></a><figcaption><a class="button primary" href="{e(config['instagramUrl'])}" target="_blank" rel="noopener noreferrer">{t('instaButton')}</a></figcaption></figure><div><p class="eyebrow">{t('aboutTag')}</p><h2>{t('aboutTitle')}</h2><p>{t('aboutText')}</p><p>{t('aboutText2')}</p><a class="text-link" href="#notice">{t('noticeLink')} ↗</a></div></section>
<section class="container payment" id="payment"><div><p class="eyebrow">{t('paymentTag')}</p><h2>{t('paymentTitle')}</h2><p>{t('paymentText')}</p><p class="small-note">{t('paymentNote')}</p></div><a class="qr-card" href="qr.png" target="_blank" rel="noopener"><img src="qr.png" width="220" height="220" loading="lazy" alt="{'मौजूदा भुगतान QR कोड' if n==0 else 'Existing payment QR code'}"><span>{t('qr')}</span></a></section>
<section class="section container" id="contact"><div class="section-heading"><p class="eyebrow">{t('contactTag')}</p><h2>{t('contactTitle')}</h2><p>{t('contactText')}</p></div><div class="contact-grid"><article><span class="contact-number">01 / FORM</span><h3>{t('formTitle')}</h3><p>{t('formAvailable') if form else t('formUnavailable')}</p>{formcta}</article><article><span class="contact-number">02 / INSTAGRAM</span><h3>@baalrishi_jyotish</h3><p>{t('instaText')}</p><a class="button primary" href="{config['instagramUrl']}" target="_blank" rel="noopener noreferrer">{t('instaButton')}</a></article></div><p class="privacy-note">{t('privacy')}</p></section>
<section class="container faq"><h2>{t('faqTitle')}</h2><div>{faqs}</div></section>
<section class="container section" id="languages"><div class="language-panel"><div><p class="eyebrow">LANGUAGES</p><h2>{t('langTitle')}</h2><p>{t('langText')}</p></div><div><div class="native-languages"><a href="index.html" lang="hi" hreflang="hi" {'aria-current="page"' if n==0 else ''}>हिन्दी</a><a href="en.html" lang="en" hreflang="en" {'aria-current="page"' if n==1 else ''}>English</a></div><div id="google_translate_element" class="google-translate-widget"></div></div></div></section>
<aside class="container notice" id="notice"><h2>ⓘ {t('noticeTitle')}</h2><p>{t('notice')}</p></aside></main>
<footer><div class="container footer-inner"><div class="brand"><span class="brand-mark" aria-hidden="true">✺</span><span><strong>{'बाल ऋषि' if n==0 else 'Baal Rishi'}</strong><small>{t('footer')}</small></span></div><p>© <span id="year">2026</span> Baal Rishi</p><a href="#home">{'ऊपर जाएँ ↑' if n==0 else 'Back to top ↑'}</a></div></footer>
<script>function googleTranslateElementInit(){{new google.translate.TranslateElement({{pageLanguage:'{lang}',includedLanguages:'{INCLUDED_LANGS}',layout:google.translate.TranslateElement.InlineLayout.SIMPLE,autoDisplay:false}},'google_translate_element')}}</script>
<script src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit" async></script>
</body></html>'''
 (ROOT/('index.html' if n==0 else 'en.html')).write_text(html.replace('><', '>\n<') + '\n')
print('Built Hindi and English pages with',len(services),'services; Google Form configured:',bool(form))
