"""Build both static language pages. Run: python3 scripts/build.py"""
from pathlib import Path
from html import escape as e
import json, hashlib, base64
ROOT = Path(__file__).resolve().parent.parent
config = json.loads((ROOT / 'site-config.json').read_text())
# Each service: id, number, symbol, title, description, options, what to prepare, what is included, process, benefits.
# Options: (Hindi name, English name, fee in ₹, Hindi detail, English detail). Edit fees here.
services = [
('kundali','01','◇',
 ['जन्म कुंडली एवं राशि उपाय','Janam Kundli & Rashi Remedies'],
 ['अपनी जन्म कुंडली को पारंपरिक वैदिक ज्योतिष से समझें—लग्न, राशि, नक्षत्र, ग्रह दशा—और अपनी राशि के अनुसार सरल, सात्त्विक उपाय जानें।','Understand your birth chart (janam kundli) through traditional Vedic astrology—ascendant, moon sign, nakshatra and dasha—with simple remedies suited to your rashi.'],
 [('राशि अनुसार सरल उपाय','Remedies for your rashi',101,'आपकी चंद्र राशि के अनुसार दैनिक जीवन के सरल उपाय—मंत्र, शुभ दिन, रंग और दान।','Simple everyday remedies for your moon sign—mantra, favourable day, colour and charity.'),
  ('एक प्रश्न – कुंडली से','One question from your kundli',151,'करियर, विवाह, धन या परिवार—किसी एक प्रश्न पर केंद्रित पारंपरिक दृष्टिकोण।','A focused traditional perspective on one question—career, marriage, money or family.'),
  ('कुंडली परिचय','Kundli overview',251,'लग्न, राशि, नक्षत्र और मुख्य ग्रह स्थिति का सरल भाषा में परिचय।','Your ascendant, moon sign, nakshatra and key planetary positions explained simply.'),
  ('विस्तृत कुंडली विश्लेषण + उपाय','Detailed kundli reading + remedies',551,'बारह भाव, वर्तमान दशा और जीवन के प्रमुख विषयों पर विस्तृत चर्चा, राशि अनुसार उपायों के साथ।','All twelve houses, your current dasha and key life themes in depth, with rashi-based remedies.'),
  ('वर्षफल – आने वाला वर्ष','Varshphal – the year ahead',1100,'आने वाले 12 महीनों के लिए ग्रह गोचर और दशा का पारंपरिक अध्ययन।','A traditional study of transits and dasha for the next 12 months.'),
  ('सम्पूर्ण जीवन कुंडली परामर्श','Complete life kundli consultation',2100,'करियर, संबंध, परिवार और धन—सभी विषयों पर लंबा, विस्तृत परामर्श।','A long, in-depth consultation across career, relationships, family and finances.')],
 ['जन्म तिथि, यथासंभव सही जन्म समय, जन्म स्थान और आपके मुख्य सवाल। केवल राशि उपाय के लिए अपनी राशि या जन्म तिथि काफ़ी है।','Your birth date, time as accurately as known, birthplace and main questions. For rashi remedies alone, your moon sign or birth date is enough.'],
 ['चुने गए विकल्प के अनुसार ग्रहों, भावों और दशा का पारंपरिक अध्ययन, आपके विषयों पर चर्चा और राशि अनुसार सरल उपाय।','A traditional reading of planets, houses and dasha for your chosen option, discussion of your topics and simple rashi-based remedies.'],
 ['जन्म विवरण की पुष्टि के बाद कुंडली बनाकर चर्चा की जाती है। जन्म समय पता न हो तो पहले बताएं। उपाय पूरी तरह स्वैच्छिक हैं।','Your chart is prepared and discussed after your birth details are confirmed. Tell us first if your birth time is uncertain. Remedies are entirely voluntary.'],
 [['अपनी कुंडली और जीवन के प्रमुख विषयों की स्पष्ट, व्यवस्थित समझ','आपकी राशि के अनुसार अपनाने में आसान उपाय','₹101 से शुरू—अपनी ज़रूरत के अनुसार विकल्प चुनें','निर्णय से पहले एक पारंपरिक दृष्टिकोण से सोचने का मौका'],
  ['A clear, organised understanding of your chart and key life themes','Easy-to-follow remedies suited to your rashi','Starts at ₹101—choose only the depth you need','A traditional perspective to consider before you decide']]),
('palm','02','<svg viewBox="0 0 24 24"><path d="M18 11V6a2 2 0 0 0-4 0M14 10V4a2 2 0 0 0-4 0v2M10 10.5V6a2 2 0 0 0-4 0v8M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-6-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15"/></svg>',
 ['हस्तरेखा परामर्श','Palm Reading (Hast Rekha)'],
 ['हथेली की रेखाओं, पर्वतों और चिह्नों के माध्यम से अपने स्वभाव और जीवन के विषयों पर पारंपरिक सामुद्रिक शास्त्र का दृष्टिकोण। घर बैठे फोटो से।','A traditional samudrik shastra perspective on your nature and life themes through the lines, mounts and marks of your palm—from a photo, at home.'],
 [('एक प्रश्न – हस्तरेखा से','One question from your palm',101,'हथेली की फोटो से किसी एक प्रश्न पर संक्षिप्त चर्चा।','A short discussion of one question from a photo of your palm.'),
  ('मुख्य रेखाएँ','Main lines reading',251,'जीवन, हृदय, मस्तिष्क और भाग्य रेखा का पारंपरिक अध्ययन।','A traditional reading of the life, heart, head and fate lines.'),
  ('विस्तृत हस्तरेखा','Detailed palm reading',551,'दोनों हाथ, पर्वत, विशेष चिह्न और अंगुलियों का विस्तृत अध्ययन।','Both hands, mounts, special marks and fingers studied in detail.'),
  ('हस्तरेखा + कुंडली संयुक्त','Palm + kundli combined',1100,'हस्तरेखा और जन्म कुंडली—दोनों को मिलाकर एक समग्र दृष्टिकोण।','Your palm and birth chart read together for a fuller perspective.')],
 ['दोनों हथेलियों की साफ़, अच्छी रोशनी में ली गई फोटो (उंगलियाँ खुली हुई) और आपका प्रश्न। संयुक्त विकल्प के लिए जन्म विवरण भी।','Clear, well-lit photos of both palms with fingers open, and your question. For the combined option, your birth details too.'],
 ['चुने गए विकल्प के अनुसार रेखाओं, पर्वतों और चिह्नों की चर्चा, और इच्छानुसार सामान्य सात्त्विक उपाय।','Discussion of lines, mounts and marks for your chosen option, and optional general remedies.'],
 ['फोटो स्पष्ट होने की पुष्टि के बाद परामर्श होता है। हस्तरेखा एक पारंपरिक मान्यता है; इससे आयु, रोग या किसी घटना की निश्चित भविष्यवाणी नहीं की जाती।','The consultation follows once your photos are confirmed clear. Palmistry is a traditional belief; it is not used to predict lifespan, illness or any certain event.'],
 [['अपने स्वभाव और क्षमताओं पर एक नया नज़रिया','सही जन्म समय पता न हो तब भी संभव','घर बैठे फोटो से आसान शुरुआत','कुंडली के साथ मिलाकर गहरी समझ'],
  ['A fresh perspective on your nature and strengths','Possible even without an exact birth time','An easy start from home with a photo','Deeper insight when combined with your kundli']]),
('relationships','03','♡',
 ['प्रेम, विवाह एवं कुंडली मिलान','Love, Marriage & Kundli Milan'],
 ['प्रेम, रिश्तों और विवाह से जुड़े प्रश्नों पर पारंपरिक दृष्टिकोण—गुण मिलान और मांगलिक विचार सहित। निर्णय में आपकी इच्छा और आपसी सहमति सबसे महत्वपूर्ण है।','A traditional perspective on love, relationships and marriage—including gun milan and manglik analysis. Personal choice and mutual consent always come first.'],
 [('प्रेम एवं संबंध प्रश्न','Love & relationship question',251,'रिश्ते की उलझनों पर संवेदनशील, बिना जजमेंट की बातचीत।','A sensitive, non-judgmental conversation about a relationship concern.'),
  ('विवाह योग एवं समय','Marriage prospects & timing',551,'आपकी कुंडली में विवाह से जुड़े पारंपरिक संकेतों और समय पर चर्चा।','Traditional marriage indicators and timing in your kundli discussed.'),
  ('कुंडली मिलान (36 गुण)','Kundli milan (36 gun)',1100,'दोनों की कुंडली का अष्टकूट गुण मिलान और मुख्य बिंदुओं पर चर्चा।','Ashtakoot gun matching of both charts and a discussion of the key points.'),
  ('विस्तृत मिलान + मांगलिक विचार + उपाय','Detailed matching + manglik + remedies',2100,'गुण मिलान, मांगलिक दोष विचार, ग्रह मैत्री और सुझाए गए उपाय।','Gun milan, manglik dosha analysis, planetary compatibility and suggested remedies.')],
 ['अपने जन्म विवरण और प्रश्न। मिलान के लिए दूसरे व्यक्ति की जानकारी केवल उनकी सहमति से साझा करें। निजी चैट भेजने की आवश्यकता नहीं है।','Your birth details and question. For matching, share the other person’s details only with their consent. You do not need to send private chats.'],
 ['चुने गए विकल्प के अनुसार विवाह के संकेतों, गुण मिलान और अपेक्षाओं पर चर्चा, और इच्छानुसार सामान्य उपाय।','Discussion of marriage indicators, gun milan and expectations for your chosen option, with optional general remedies.'],
 ['पहले प्रश्न और उपलब्ध विवरण समझे जाते हैं, फिर दायरा तय होता है। किसी विवाह, तिथि या रिश्ते के परिणाम की गारंटी नहीं है; किसी को नियंत्रित करने, वशीकरण या प्रेम वापस लाने का दावा नहीं किया जाता।','We first understand your question and details, then agree on the scope. No marriage, date or relationship outcome is guaranteed, and we never offer to control another person or bring someone back.'],
 [['रिश्ते की उलझन को बिना जजमेंट के समझने का मौका','विवाह से पहले गुण मिलान पर पारंपरिक स्पष्टता','परिवार या साथी से बातचीत के लिए बेहतर तैयारी','अपने निर्णय पर भरोसा बढ़ाने वाली सोच-समझ'],
  ['A non-judgmental space to understand a relationship concern','Traditional clarity on gun milan before marriage','Better preparation for conversations with family or a partner','Greater confidence in your own decision']]),
('family','04','⌂',
 ['संतान एवं परिवार मार्गदर्शन','Children & Family Guidance'],
 ['बच्चों और परिवार से जुड़े प्रश्नों पर आस्था-आधारित मार्गदर्शन—नक्षत्र अनुसार नामाक्षर, बाल कुंडली और शिक्षा की दिशा सहित।','Faith-based guidance for questions about children and family—including baby name letters by nakshatra, a child’s kundli and education direction.'],
 [('नामाक्षर सुझाव (नक्षत्र अनुसार)','Baby name letters (by nakshatra)',151,'जन्म नक्षत्र के अनुसार शुभ नामाक्षर और नाम के विचार।','Auspicious starting letters and name ideas from the birth nakshatra.'),
  ('बाल कुंडली','Child’s kundli',551,'बच्चे के स्वभाव, रुचियों और मुख्य ग्रह स्थिति का पारंपरिक अध्ययन।','A traditional look at a child’s nature, interests and key planetary positions.'),
  ('शिक्षा एवं करियर दिशा','Education & career direction',1100,'बच्चों और युवाओं के लिए विषय और करियर चुनने पर पारंपरिक दृष्टिकोण।','A traditional perspective for children and young people choosing subjects and careers.'),
  ('संतान एवं पारिवारिक प्रश्न','Children & family questions',1100,'परिवार और संतान से जुड़े प्रश्नों पर शांत, सहानुभूतिपूर्ण चर्चा।','A calm, empathetic discussion of questions about family and children.')],
 ['आपके प्रश्न और आवश्यक जन्म विवरण (बच्चे के लिए उसका जन्म विवरण)। चिकित्सा रिपोर्ट भेजने की आवश्यकता नहीं है।','Your questions and the birth details needed (for a child, the child’s details). Medical reports are not required.'],
 ['चुने गए विकल्प के अनुसार पारिवारिक विषयों पर पारंपरिक ज्योतिषीय चर्चा और इच्छानुसार प्रार्थना या ध्यान की सामान्य जानकारी।','Traditional astrological discussion of family themes for your chosen option, with optional general information about prayer or meditation.'],
 ['पहले अपेक्षाएं और सीमाएं स्पष्ट की जाती हैं। यह प्रजनन उपचार नहीं है; गर्भधारण, संतान या शिशु के लिंग की भविष्यवाणी या गारंटी नहीं दी जाती। करियर पर चर्चा योग्य शिक्षकों या काउंसलर की सलाह का विकल्प नहीं है।','We first clarify expectations and limits. This is not fertility treatment; we do not predict or guarantee conception, children or a baby’s sex. Career discussion is not a substitute for qualified teachers or counsellors.'],
 [['नवजात के लिए शुभ नामाक्षर की पारंपरिक जानकारी','बच्चे के स्वभाव और रुचियों को समझने का नया नज़रिया','चिंता के समय भावनात्मक सहारा और सुनने वाला कोई','अपेक्षाओं और सीमाओं की शुरुआत में ही स्पष्टता'],
  ['Traditional guidance on auspicious name letters for a newborn','A fresh view of your child’s nature and interests','Emotional support and a listening ear in anxious times','Clarity on expectations and limits from the start']]),
('mantra','05','✺',
 ['मंत्र, ध्यान एवं साधना','Mantra, Meditation & Sadhana'],
 ['दैनिक जीवन में एक सरल आध्यात्मिक अभ्यास के लिए आपकी राशि और ग्रह स्थिति के अनुसार पारंपरिक मंत्र, जप, ध्यान और पूजा विधि का मार्गदर्शन।','Guidance on traditional mantra, chanting, meditation and puja suited to your rashi and planets, for a simple spiritual practice in everyday life.'],
 [('राशि/ग्रह अनुसार मंत्र','Mantra for your rashi or planet',151,'आपकी राशि या ग्रह स्थिति के अनुसार एक सरल मंत्र और जप की संख्या।','A simple mantra and chanting count suited to your rashi or planets.'),
  ('व्यक्तिगत मंत्र एवं जप विधि','Personal mantra & chanting method',551,'आपकी परंपरा और दिनचर्या के अनुसार मंत्र, माला और जप की सही विधि।','A mantra, mala and chanting method suited to your tradition and routine.'),
  ('21 दिन ध्यान एवं साधना योजना','21-day meditation & sadhana plan',1100,'तीन सप्ताह की सरल दैनिक योजना, बीच में मार्गदर्शन के साथ।','A simple three-week daily plan with guidance along the way.'),
  ('ग्रह शांति – पूजा विधि मार्गदर्शन','Graha shanti – puja guidance',2100,'ग्रह शांति के पारंपरिक पूजा या पाठ की विधि और सामग्री की जानकारी, जिसे आप स्वयं कर सकें।','How to perform traditional graha shanti puja or path yourself, with the items needed.'),
  ('वार्षिक आध्यात्मिक मार्गदर्शन','Annual spiritual guidance',5100,'12 महीने तक हर माह एक परामर्श—कुंडली, मंत्र और साधना पर निरंतर मार्गदर्शन।','One consultation every month for 12 months—ongoing guidance on kundli, mantra and practice.')],
 ['आपकी रुचि, परंपरा और अभ्यास के लिए उपलब्ध समय; ग्रह अनुसार मंत्र के लिए राशि या जन्म विवरण। किसी विशेष धार्मिक मान्यता को अपनाना आवश्यक नहीं है।','Your interests, tradition and the time you can set aside; your rashi or birth details for planet-based mantras. You are not required to adopt any particular belief.'],
 ['चुने गए विकल्प के अनुसार अभ्यास की विधि, सहज दिनचर्या बनाने पर चर्चा और अपने सहज स्तर पर अभ्यास का मार्गदर्शन।','The method for your chosen option, help building a manageable routine and guidance on practising at your own comfort level.'],
 ['आपके अनुभव के अनुसार अभ्यास तय होता है। भागीदारी स्वैच्छिक है; चमत्कार, रोगमुक्ति या निश्चित परिणाम का दावा नहीं है।','Your practice is set according to your experience. Participation is voluntary; no miracle, cure or specific result is promised.'],
 [['रोज़ के जीवन में शामिल करने योग्य सरल आध्यात्मिक अभ्यास','अपनी राशि और ग्रहों के अनुसार चुना गया मंत्र','मानसिक शांति और नियमित दिनचर्या बनाने में सहायता','लंबे समय तक साथ चलने वाला मार्गदर्शन (वार्षिक विकल्प)'],
  ['A simple spiritual practice you can build into daily life','A mantra chosen for your rashi and planets','Support in building a calm, regular routine','Ongoing guidance over time (annual option)']])]

# Moon-sign remedies: symbol, Hindi, English, ruling planet (hi, en), day (hi, en), mantra, remedy (hi, en).
rashis = [
('♈︎','मेष','Aries','मंगल','Mars','मंगलवार','Tuesday','ॐ अं अंगारकाय नमः','मंगलवार को हनुमान चालीसा का पाठ करें और लाल मसूर का दान करें।','Recite the Hanuman Chalisa on Tuesdays and donate red lentils.'),
('♉︎','वृषभ','Taurus','शुक्र','Venus','शुक्रवार','Friday','ॐ शुं शुक्राय नमः','शुक्रवार को चावल या दूध जैसी सफ़ेद वस्तुओं का दान करें और माँ लक्ष्मी का स्मरण करें।','Donate white items such as rice or milk on Fridays and remember Goddess Lakshmi.'),
('♊︎','मिथुन','Gemini','बुध','Mercury','बुधवार','Wednesday','ॐ बुं बुधाय नमः','बुधवार को गाय को हरा चारा खिलाएँ और गणेश जी की पूजा करें।','Feed green fodder to a cow on Wednesdays and worship Lord Ganesha.'),
('♋︎','कर्क','Cancer','चंद्र','Moon','सोमवार','Monday','ॐ सों सोमाय नमः','सोमवार को शिवलिंग पर जल या दूध अर्पित करें और माता का आशीर्वाद लें।','Offer water or milk to the Shivling on Mondays and seek your mother’s blessings.'),
('♌︎','सिंह','Leo','सूर्य','Sun','रविवार','Sunday','ॐ घृणि सूर्याय नमः','प्रतिदिन सूर्योदय के समय सूर्य को जल अर्पित करें और पिता का सम्मान करें।','Offer water to the rising sun each morning and honour your father.'),
('♍︎','कन्या','Virgo','बुध','Mercury','बुधवार','Wednesday','ॐ बुं बुधाय नमः','बुधवार को हरी मूंग का दान करें और विद्यार्थियों की सहायता करें।','Donate green moong on Wednesdays and help students.'),
('♎︎','तुला','Libra','शुक्र','Venus','शुक्रवार','Friday','ॐ शुं शुक्राय नमः','शुक्रवार को स्वच्छ, सुगंधित वस्त्र पहनें और कन्याओं को मिठाई दें।','Wear clean, lightly fragranced clothes on Fridays and offer sweets to young girls.'),
('♏︎','वृश्चिक','Scorpio','मंगल','Mars','मंगलवार','Tuesday','ॐ अं अंगारकाय नमः','मंगलवार को हनुमान जी को सिंदूर अर्पित करें और गुड़ का दान करें।','Offer sindoor to Lord Hanuman on Tuesdays and donate jaggery.'),
('♐︎','धनु','Sagittarius','गुरु','Jupiter','गुरुवार','Thursday','ॐ बृं बृहस्पतये नमः','गुरुवार को चना दाल या हल्दी जैसी पीली वस्तुओं का दान करें और गुरुजनों का आदर करें।','Donate yellow items such as chana dal or turmeric on Thursdays and respect your teachers.'),
('♑︎','मकर','Capricorn','शनि','Saturn','शनिवार','Saturday','ॐ शं शनैश्चराय नमः','शनिवार को पीपल के नीचे सरसों के तेल का दीपक जलाएँ और ज़रूरतमंदों की मदद करें।','Light a mustard-oil lamp under a peepal tree on Saturdays and help those in need.'),
('♒︎','कुंभ','Aquarius','शनि','Saturn','शनिवार','Saturday','ॐ शं शनैश्चराय नमः','शनिवार को काले तिल का दान करें और श्रमिकों के प्रति दयालु रहें।','Donate black sesame on Saturdays and be kind to workers.'),
('♓︎','मीन','Pisces','गुरु','Jupiter','गुरुवार','Thursday','ॐ बृं बृहस्पतये नमः','गुरुवार को केले के वृक्ष की पूजा करें और धार्मिक पुस्तकों का दान करें।','Worship a banana tree on Thursdays and donate spiritual books.')]
# Privacy notice (Digital Personal Data Protection Act, 2023). Each section: (heading, [paragraphs]).
PRIVACY_UPDATED=['29 सितंबर 2026','29 September 2026']
CONTACT_EMAIL='pandeyravidev2@gmail.com'
privacy=[
[('हम कौन हैं','Antarodaya / अंतरोदय (antarodaya.in) पारंपरिक ज्योतिष और आध्यात्मिक परामर्श की सेवा है। इस नीति में बताया गया है कि वेबसाइट पर लॉगिन, अनुभव (रिव्यू) और परामर्श के लिए आपकी कौन-सी जानकारी ली जाती है और उसका उपयोग कैसे होता है।'),
 ('हम कौन-सी जानकारी लेते हैं','• खाता: आपका नाम, ईमेल और (Google से लॉगिन करने पर) प्रोफ़ाइल फोटो।<br>• अनुभव: आपकी रेटिंग, लिखा हुआ अनुभव, चुनी गई सेवा और दिखने वाला नाम।<br>• बुकिंग: चुनी गई तारीख और समय, WhatsApp/फ़ोन नंबर, बात करने का तरीका और आपका प्रश्न।<br>• परामर्श: फॉर्म या Instagram पर आप जो विवरण भेजते हैं, जैसे जन्म तिथि, समय, स्थान, हथेली की फोटो और आपका प्रश्न।<br>हम भुगतान कार्ड, UPI PIN, OTP या बैंक पासवर्ड कभी नहीं लेते।'),
 ('उपयोग का उद्देश्य','लॉगिन करवाना, आपका अनुभव दिखाना और उसका उत्तर देना, बुकिंग की पुष्टि करना, परामर्श देना और आपसे संपर्क करना। हम आपकी जानकारी बेचते नहीं हैं और विज्ञापन के लिए उपयोग नहीं करते।'),
 ('सहमति','लॉगिन करके और अनुभव भेजते समय सहमति का बॉक्स चुनकर आप इस नीति के अनुसार जानकारी के उपयोग की सहमति देते हैं। आप कभी भी सहमति वापस ले सकते हैं: अपना अनुभव या पूरा खाता हटा दें।'),
 ('जानकारी कहाँ रखी जाती है','लॉगिन और अनुभव Google Firebase पर भारत (मुंबई, asia-south1) में रखे जाते हैं। परामर्श फॉर्म Google Forms पर, संदेश Instagram पर और वेबसाइट GitHub Pages पर होस्ट है। इन सेवाओं पर उनकी अपनी गोपनीयता नीतियाँ भी लागू होती हैं।'),
 ('कितने समय तक','प्रकाशित अनुभव वेबसाइट पर तब तक रहते हैं जब तक आप उन्हें हटा नहीं देते। जो अनुभव प्रकाशित नहीं हुए या छिपा दिए गए, वे 30 दिन बाद अपने आप मिट जाते हैं। जिस प्रोफ़ाइल से 30 दिन तक लॉगिन नहीं हुआ, वह भी अपने आप मिट जाती है। हर बुकिंग परामर्श की तारीख के 30 दिन बाद अपने आप मिट जाती है। बुकिंग की सूचना हमारी निजी Google Sheet और ईमेल में भी जाती है। परामर्श के लिए भेजा गया विवरण परामर्श पूरा होने के बाद ज़रूरत न रहने पर हटा दिया जाता है।'),
 ('आपके अधिकार','आप अपनी जानकारी देख, सुधार और हटा सकते हैं। "मेरा खाता" पेज पर अपना नाम बदलें, अपना अनुभव बदलें या हटाएँ, या "मेरा खाता हटाएँ" दबाकर खाता और सभी अनुभव तुरंत मिटा दें। किसी और मदद के लिए नीचे दिए ईमेल पर लिखें।'),
 ('बच्चे','खाता और अनुभव 18 वर्ष या उससे अधिक आयु के व्यक्तियों के लिए है। बच्चे से जुड़ी सेवा (जैसे बाल कुंडली या नामाक्षर) माता-पिता या अभिभावक ही लें।'),
 ('सुरक्षा','डेटा HTTPS से भेजा जाता है। सर्वर पर लगे नियमों के कारण हर व्यक्ति केवल अपना डेटा देख सकता है; केवल एडमिन अनुभव प्रकाशित कर सकता है। लॉगिन बनाए रखने के लिए आपके ब्राउज़र में Firebase की जानकारी सेव रहती है; हम विज्ञापन या ट्रैकिंग कुकीज़ का उपयोग नहीं करते।'),
 ('शिकायत एवं संपर्क',f'गोपनीयता से जुड़ी किसी भी शिकायत या अनुरोध के लिए ईमेल करें: {CONTACT_EMAIL}। हम 30 दिनों के भीतर उत्तर देने का प्रयास करते हैं।'),
 ('बदलाव','इस नीति में बदलाव होने पर नई तारीख के साथ यहीं अपडेट किया जाएगा।')],
[('Who we are','Antarodaya (antarodaya.in) offers traditional astrology and spiritual guidance. This notice explains what personal data we collect for login, reviews and consultations, and how we use it.'),
 ('What we collect','• Account: your name, email and, if you sign in with Google, your profile photo.<br>• Reviews: your rating, what you write, the service you chose and the name you want shown.<br>• Bookings: the date and time you pick, your WhatsApp/phone number, how you want to talk and your question.<br>• Consultations: what you send through the form or Instagram, such as birth date, time and place, palm photos and your question.<br>We never ask for card details, UPI PIN, OTP or bank passwords.'),
 ('Why we use it','To let you log in, show and reply to your review, confirm your booking, provide your consultation and contact you. We do not sell your data or use it for advertising.'),
 ('Consent','By logging in, and by ticking the consent box when you submit a review, you agree to this use of your data. You can withdraw consent at any time by deleting your review or your whole account.'),
 ('Where it is stored','Login and review data are stored with Google Firebase in India (Mumbai, asia-south1). The consultation form uses Google Forms, messages use Instagram, and the website is hosted on GitHub Pages. Their own privacy policies also apply.'),
 ('How long we keep it','Published reviews stay on the website until you delete them. Reviews that are not published, or are hidden, are deleted automatically after 30 days. A profile with no login for 30 days is also deleted automatically. Each booking is deleted 30 days after the consultation date. Booking alerts are also copied to our private Google Sheet and email. Consultation details are deleted once they are no longer needed after your consultation.'),
 ('Your rights','You can see, correct and delete your data. On the My account page you can change your name, edit or delete a review, or press "Delete my account" to erase your account and all your reviews at once. For anything else, email us at the address below.'),
 ('Children','Accounts and reviews are for people aged 18 or over. Services about a child (such as a child’s kundli or baby name letters) should be requested by a parent or guardian.'),
 ('Security','Data travels over HTTPS. Server-side rules let each person see only their own data, and only the admin can publish reviews. Firebase keeps you signed in using storage in your browser; we do not use advertising or tracking cookies.'),
 ('Grievances and contact',f'For any privacy request or complaint, email {CONTACT_EMAIL}. We aim to reply within 30 days.'),
 ('Changes','If this notice changes, the new version will be posted here with a new date.')]]
texts = {
'nav':[['सेवाएँ','राशि उपाय','प्रक्रिया','हमारे बारे में','अनुभव','संपर्क'],['Services','Rashi remedies','How it works','About','Reviews','Contact']],
'brand':['पारंपरिक ज्ञान • सहज मार्गदर्शन','Traditional wisdom • Thoughtful guidance'],
'eyebrow':['आस्था, समझ और आत्मचिंतन','FAITH. REFLECTION. PERSPECTIVE.'],
'hero':['परंपरा से जुड़ें।<br><em>खुद को समझें।</em>','Rooted in tradition.<br><em>Space to reflect.</em>'],
'desc':['जीवन के सवालों पर एक ठहराव, एक बातचीत और एक नया दृष्टिकोण। अंतरोदय के साथ जन्म कुंडली, हस्तरेखा और आध्यात्मिक परामर्श।','A moment to pause. A conversation about what matters. Explore kundli, palm reading and spiritual guidance with Antarodaya.'],
'book':['परामर्श के लिए संपर्क करें','Enquire about a consultation'],
'explore':['हमारी सेवाएँ देखें ↗','Explore our services ↗'],
'heroNote':['आस्था-आधारित मार्गदर्शन · परिणाम की गारंटी नहीं','Faith-based guidance · No guaranteed outcomes'],
'serviceTag':['आपकी जिज्ञासा, हमारा संवाद','A CONVERSATION THAT STARTS WITH YOU'],
'servicesTitle':['पाँच सेवाएँ, आपकी ज़रूरत के अनुसार विकल्प','Five services, options to suit every need'],
'servicesIntro':['हर सेवा में ₹101 से ₹5,100 तक के विकल्प हैं—उतना ही चुनें जितना आपको चाहिए। बुकिंग से पहले जानें कि क्या शामिल है, क्या जानकारी चाहिए और प्रक्रिया कैसी होगी।','Every service has options from ₹101 to ₹5,100—choose only what you need. See what is included, what to prepare and how it works before you book.'],
'details':['विवरण और प्रक्रिया','Details & process'],
'benefitsHeading':['इससे आपको क्या मिलता है','What you gain'],
'prepare':['क्या जानकारी चाहिए','What to prepare'],
'include':['क्या शामिल है','What is included'],
'process':['कैसे होगा','How it works'],
'feeNote':['विकल्प अनुसार शुल्क। अंतिम शुल्क और दायरा बुकिंग से पहले तय करें।','Fee depends on the option. Confirm the final fee and scope before booking.'],
'options':['विकल्प एवं शुल्क','Options & fees'],
'optionsDetail':['विकल्प विस्तार से','Options in detail'],
'from':['से शुरू','onwards'],
'choose':['इस सेवा के बारे में पूछें ↗','Enquire about this service ↗'],
'commonShort':['सभी सेवाओं पर नीचे दी गई महत्वपूर्ण सूचना लागू है।','The important notice below applies to every service.'],
'noticeLink':['महत्वपूर्ण सूचना पढ़ें','Read the important notice'],
'howTag':['सरल और स्पष्ट','SIMPLE & CONSIDERED'],
'howTitle':['परामर्श तक, तीन आसान कदम','Your consultation, in three steps'],
'steps':[[('सेवा चुनें','विवरण पढ़ें और वह सेवा चुनें जो आपके प्रश्न से संबंधित हो।'),('समय बुक करें','शनिवार या रविवार का खाली समय चुनें, या फॉर्म/Instagram से संपर्क करें। शुल्क, माध्यम और रद्द करने की शर्तें पहले तय होंगी।'),('फिर परामर्श लें','पुष्टि के बाद ही भुगतान करें और तय माध्यम पर परामर्श में शामिल हों।')],[('Explore a service','Read the details and choose the service that relates to your question.'),('Book a time','Pick a free Saturday or Sunday slot, or contact us by form or Instagram. The fee, format and cancellation terms are agreed first.'),('Join your consultation','Pay only after confirmation and join through the agreed consultation format.')]],
'aboutTag':['अंतरोदय के बारे में','ABOUT ANTARODAYA'],
'aboutTitle':['परंपरा का सम्मान।<br>आपकी समझ को महत्व।','Respect for tradition.<br>Room for your own judgment.'],
'aboutText':['अंतरोदय पारंपरिक ज्योतिष, कुंडली अध्ययन और आध्यात्मिक अभ्यास से जुड़े विषयों पर परामर्श का स्थान है। हमारा उद्देश्य आपकी जिज्ञासाओं पर संवाद और आत्मचिंतन में सहायता करना है।','Antarodaya is a space for consultation on traditional astrology, birth-chart interpretation and spiritual practice. Our purpose is to support conversation and personal reflection around your questions.'],
'aboutText2':['आपके निर्णय आपके हैं। किसी भी अभ्यास में भाग लेना स्वैच्छिक है। हम भय, चमत्कार या निश्चित भविष्य के वादे के आधार पर सेवा नहीं देते।','Your decisions remain your own. Every practice is voluntary. Our services are not based on fear, miracles or promises of a certain future.'],
'illustration':['अंतरोदय — परामर्शदाता का चित्र','Antarodaya — consultant portrait'],
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
'privacy':['केवल आवश्यक जानकारी साझा करें। सार्वजनिक टिप्पणी में जन्म विवरण, भुगतान विवरण या निजी समस्याएं न लिखें। Google Forms, Instagram और Google Firebase (लॉगिन व रिव्यू) पर उनकी अपनी गोपनीयता नीतियां लागू होती हैं।','Share only the information needed. Do not post birth details, payment information or personal concerns in public comments. Google Forms, Instagram and Google Firebase (login and reviews) apply their own privacy policies.'],
'faqTitle':['आपके कुछ सवाल','A few common questions'],
'faqs':[[('क्या किसी परिणाम की गारंटी है?','नहीं। यह पारंपरिक और आस्था-आधारित मार्गदर्शन है। निश्चित भविष्य, विवाह, सफलता, संतान, रोगमुक्ति या किसी अन्य परिणाम की गारंटी नहीं दी जाती।'),('परामर्श कब और किस माध्यम से होगा?','उपलब्ध समय, माध्यम, अवधि और भाषा संपर्क के बाद तय होंगे। वेबसाइट का अनुवाद होना उस भाषा में परामर्श उपलब्ध होने की पुष्टि नहीं है।'),('कौन-सा विकल्प चुनूँ?','एक विशेष प्रश्न हो तो ₹101–₹151 का विकल्प काफ़ी है। पूरी समझ के लिए विस्तृत विकल्प चुनें। उलझन हो तो पहले संपर्क करें—हम सही विकल्प चुनने में मदद करेंगे।'),('हस्तरेखा के लिए क्या भेजना होगा?','दोनों हथेलियों की साफ़, अच्छी रोशनी में ली गई फोटो, उंगलियाँ खुली हुई। फोटो केवल परामर्श के लिए उपयोग होती है।'),('जन्म का सही समय पता न हो तो?','बुकिंग से पहले बता दें। उपलब्ध जानकारी के आधार पर सेवा उपयुक्त है या नहीं और उसकी सीमाएं क्या होंगी, यह पहले स्पष्ट करें।'),('भुगतान और रिफंड के बारे में कैसे जानें?','भुगतान से पहले अंतिम शुल्क और रद्द करने, पुनर्निर्धारण तथा रिफंड की शर्तें लिखित रूप में पूछ लें। वेबसाइट पर तत्काल बुकिंग की सुविधा नहीं है।')],[('Are any outcomes guaranteed?','No. This is traditional, faith-based guidance. We do not guarantee a certain future, marriage, success, children, healing or any other outcome.'),('When and how will the consultation happen?','Availability, format, duration and consultation language are agreed after you contact us. A translated website does not confirm that consultations are available in that language.'),('Which option should I choose?','For one specific question, the ₹101–₹151 options are enough. For a fuller picture, choose a detailed option. Not sure? Contact us first and we will help you choose.'),('What do I send for palm reading?','Clear, well-lit photos of both palms with fingers open. Photos are used only for your consultation.'),('What if I do not know my birth time?','Tell us before booking. First clarify whether the service is suitable with the available information and what its limitations will be.'),('What about payment and refunds?','Ask for the final fee and the cancellation, rescheduling and refund terms in writing before paying. This website does not offer instant booking.')]],
'noticeTitle':['महत्वपूर्ण सूचना — सभी सेवाओं के लिए','Important notice — applies to every service'],
'notice':['यहां दी गई सेवाएं पारंपरिक मान्यताओं, ज्योतिष और आध्यात्मिक अभ्यास पर आधारित हैं; इन्हें वैज्ञानिक रूप से प्रमाणित भविष्यवाणी न मानें। हम किसी घटना, निश्चित भविष्य, सफलता, विवाह, संतान, रोगमुक्ति, चमत्कार या अन्य परिणाम का दावा या गारंटी नहीं देते। यह चिकित्सा, मानसिक स्वास्थ्य उपचार, कानूनी या वित्तीय सलाह का विकल्प नहीं है। इन विषयों के लिए योग्य पेशेवर से संपर्क करें; निर्धारित उपचार न रोकें। व्यक्तिगत निर्णय अपने विवेक से लें।','These services are based on traditional beliefs, astrology and spiritual practices; they should not be treated as scientifically established predictions. We do not claim or guarantee any event, certain future, success, marriage, children, cure, miracle or other outcome. This is not a substitute for medical care, mental health treatment, legal advice or financial advice. Consult qualified professionals for those matters and do not stop prescribed treatment. Use your own judgment when making decisions.'],
'langTitle':['दूसरी भाषा में पढ़ें','Read in another language'],
'langText':['Google द्वारा स्वचालित अनुवाद। इसमें त्रुटियां हो सकती हैं; शुल्क और सेवा की पुष्टि हमसे करें।','Automatic translation by Google. It may contain errors; confirm fees and service details with us.'],
'metaTitle':['अंतरोदय | ऑनलाइन जन्म कुंडली, हस्तरेखा, कुंडली मिलान एवं ज्योतिष परामर्श','Antarodaya | Online Kundli Reading, Palm Reading & Astrology Consultation'],
'metaDesc':['अंतरोदय पर ऑनलाइन ज्योतिष परामर्श: जन्म कुंडली विश्लेषण, राशि अनुसार उपाय, हस्तरेखा, कुंडली मिलान, नामाक्षर और मंत्र साधना। ₹101 से शुरू।','Online astrology consultation with Antarodaya: janam kundli reading, rashi remedies, palm reading, kundli milan, baby names and mantra guidance. From ₹101.'],
'rashiTag':['राशि अनुसार उपाय','REMEDIES BY RASHI'],
'rashiTitle':['अपनी राशि के सरल उपाय','Simple remedies for your rashi'],
'rashiIntro':['अपनी चंद्र राशि चुनें और उसके स्वामी ग्रह के अनुसार पारंपरिक, सात्त्विक उपाय पढ़ें। अपनी कुंडली के अनुसार व्यक्तिगत उपाय केवल ₹101 में।','Find your moon sign (rashi) and read traditional, gentle remedies based on its ruling planet. Personal remedies from your own kundli start at just ₹101.'],
'rashiLord':['स्वामी','Ruled by'],
'rashiMantra':['मंत्र','Mantra'],
'rashiNote':['ये सामान्य पारंपरिक सुझाव हैं और पूरी तरह स्वैच्छिक हैं; इनसे किसी परिणाम की गारंटी नहीं है। सही राशि के लिए अपनी जन्म कुंडली देखें।','These are general traditional suggestions and entirely voluntary; they do not guarantee any outcome. Check your birth chart to confirm your moon sign.'],
'rashiCta':['मेरी राशि के व्यक्तिगत उपाय – ₹101','Personal remedies for my rashi – ₹101'],
'meaningLabel':['अंतरोदय का अर्थ','What Antarodaya means'],
'meaning':[['<strong>अंतर</strong> (भीतर, अंतर्मन) + <strong>उदय</strong> (जागरण, सूर्योदय) = <em>भीतर का उदय</em>।','जैसे सूर्य हर सुबह अंधकार दूर करता है, वैसे ही अंतरोदय का उद्देश्य है—जन्म कुंडली, हस्तरेखा और मंत्र-साधना के माध्यम से आपके मन में स्पष्टता, शांति और आत्मविश्वास का उदय।','हमारे चिह्न में कमल से उगता सूर्य इसी का प्रतीक है: कमल—शुद्ध अंतर्मन, सूर्य—नई समझ का प्रकाश।'],['<strong>Antar</strong> (within, the inner self) + <strong>Udaya</strong> (rising, dawn) = <em>the rising within</em>.','Just as the sun clears the darkness each morning, Antarodaya exists to help clarity, calm and confidence rise within you—through kundli, palm reading and mantra practice.','Our mark shows a sun rising from a lotus: the lotus for a pure inner self, the sun for the light of new understanding.']],
'reviewsTag':['लोगों के अनुभव','IN THEIR OWN WORDS'],
'reviewsTitle':['जिन्होंने हम पर भरोसा किया','Experiences from people we have guided'],
'reviewsIntro':['हर अनुभव लॉगिन किए हुए ग्राहक द्वारा लिखा गया है और प्रकाशित होने से पहले जाँचा जाता है। अनुभव व्यक्तिगत हैं; ये किसी परिणाम की गारंटी नहीं हैं।','Every experience is written by a signed-in client and checked before it is published. Experiences are personal and are not a guarantee of any outcome.'],
'writeReview':['अपना अनुभव लिखें','Write about your experience'],
'moderationNote':['लिखने के लिए लॉगिन ज़रूरी है। प्रकाशन से पहले हर अनुभव की जाँच होती है।','Log in to write. Every experience is checked before it is published.'],
'overall':['कुल रेटिंग','Overall rating'],
'reviewsLoading':['अनुभव लोड हो रहे हैं…','Loading experiences…'],
'noscript':['रिव्यू और लॉगिन के लिए JavaScript चालू करें।','Turn on JavaScript to see reviews and log in.'],
'accountTitle':['मेरा खाता','My account'],
'adminTitle':['एडमिन पैनल','Admin panel'],
'login':['लॉगिन','Log in'],
'bookTag':['समय तय करें','BOOK A TIME'],
'bookTitle':['अपना परामर्श समय चुनें','Choose your consultation time'],
'bookIntro':['शनिवार और रविवार को सुबह 9–12, दोपहर 2–5 और रात 8–11 बजे (भारतीय समय)। समय चुनें, अनुरोध भेजें, और हम ईमेल व WhatsApp पर पुष्टि करेंगे।','Saturdays and Sundays, 9 am–12 pm, 2–5 pm and 8–11 pm (India time). Pick a time and send a request, and we will confirm by email and WhatsApp.'],
'hours':['परामर्श का समय','Consultation hours'],
'hoursText':['शनिवार–रविवार · सुबह 9–12 · दोपहर 2–5 · रात 8–11 (IST)','Sat–Sun · 9 am–12 pm · 2–5 pm · 8–11 pm (IST)'],
'connect':['हमसे जुड़ें','Connect with us'],
'privacyTitle':['गोपनीयता नीति','Privacy policy'],
'privacyUpdated':['अंतिम अपडेट','Last updated'],
'skip':['सीधे सामग्री पर जाएँ','Skip to content'],
'footer':['आस्था के साथ, विवेक भी।','A place for faith. A space for reflection.']
}
BASE='https://antarodaya.in/'
BRAND=['अंतरोदय','Antarodaya']
from urllib.parse import urlparse
import re
form=config.get('googleFormUrl','').strip()
if form:
 u=urlparse(form)
 if u.scheme!='https' or u.hostname not in ('docs.google.com','forms.gle') or (u.hostname=='docs.google.com' and (not u.path.startswith('/forms/') or '/edit' in u.path)): raise ValueError('Use a public HTTPS Google Forms responder link')
INCLUDED_LANGS='hi,en,bn,bho,mr,gu,ta,te,kn,ml,pa,ur,ar,ne,fr,es,de,pt,ja,zh-CN'
ICONS={
 'whatsapp':'<path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2c-1.5 0-3-.4-4.3-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2c0 1.3.9 2.5 1.1 2.7.1.2 1.8 2.8 4.4 3.9 1.6.7 2.3.8 3.1.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.3-.2-.5-.3Z"/>',
 'phone':'<path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1l-2.3 2.2Z"/>',
 'email':'<path d="M3 5h18a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Zm9 7.2L4.4 7H4v.4l8 5.6 8-5.6V7h-.4L12 12.2Z"/>',
 'instagram':'<path d="M12 7.3a4.7 4.7 0 1 0 0 9.4 4.7 4.7 0 0 0 0-9.4Zm0 7.7a3 3 0 1 1 0-6 3 3 0 0 1 0 6Zm6-7.9a1.1 1.1 0 1 1-2.2 0 1.1 1.1 0 0 1 2.2 0ZM21.9 8c-.1-1.6-.4-3-1.6-4.2S17.6 2.2 16 2.1H8c-1.6.1-3 .4-4.2 1.6S2.2 6.4 2.1 8v8c.1 1.6.4 3 1.6 4.2s2.6 1.5 4.2 1.6h8c1.6-.1 3-.4 4.2-1.6s1.5-2.6 1.6-4.2V8Zm-2 9.7a3.3 3.3 0 0 1-1.9 1.9c-1.3.5-4.4.4-5.9.4s-4.6.1-5.9-.4a3.3 3.3 0 0 1-1.9-1.9C3.8 16.4 3.9 13.4 3.9 12s-.1-4.4.4-5.7a3.3 3.3 0 0 1 1.9-1.9C7.4 3.9 10.5 4 12 4s4.6-.1 5.9.4a3.3 3.3 0 0 1 1.9 1.9c.5 1.3.4 4.3.4 5.7s.1 4.4-.4 5.7Z"/>',
 'facebook':'<path d="M22 12a10 10 0 1 0-11.6 9.9v-7H7.9V12h2.5V9.8c0-2.5 1.5-3.9 3.8-3.9 1.1 0 2.2.2 2.2.2v2.5h-1.3c-1.2 0-1.6.8-1.6 1.6V12h2.8l-.4 2.9h-2.4v7A10 10 0 0 0 22 12Z"/>'}
CONTACT=config.get('contact',{})
def contact_links():
 items=[('whatsapp','WhatsApp',f"https://wa.me/{CONTACT.get('whatsapp','')}"),('phone','Phone',f"tel:{CONTACT.get('phone','').replace(' ','')}"),('email','Email',f"mailto:{CONTACT.get('email','')}"),('instagram','Instagram',CONTACT.get('instagram','')),('facebook','Facebook',CONTACT.get('facebook',''))]
 out=''
 for key,label,href in items:
  ext=' target="_blank" rel="noopener noreferrer"' if href.startswith('http') else ''
  out+=f'<a class="social {key}" href="{e(href)}"{ext} aria-label="{label}" title="{label}"><svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor">{ICONS[key]}</svg></a>'
 return f'<div class="socials">{out}</div>'
PLUS_ICON='<svg class="plus-icon" viewBox="0 0 20 20" aria-hidden="true"><line x1="10" y1="3" x2="10" y2="17"/><line x1="3" y1="10" x2="17" y2="10"/></svg>'
GLOBE_ICON='<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.7 5.7 3.7 9s-1.2 6.3-3.7 9c-2.5-2.7-3.7-5.7-3.7-9S9.5 5.7 12 3Z"/></svg>'
USER_ICON='<span class="icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 12a4.5 4.5 0 1 0 0-9 4.5 4.5 0 0 0 0 9Zm0 2c-4.4 0-8 2.3-8 5.2V21h16v-1.8c0-2.9-3.6-5.2-8-5.2Z"/></svg></span>'
# Each page kind in Hindi (n=0) and English (n=1).
# English is the default (index.html); Hindi pages carry a -hi / hi prefix.
FILES={'home':['hi.html','index.html'],'account':['account-hi.html','account.html'],'admin':['admin-hi.html','admin.html'],'privacy':['privacy-hi.html','privacy.html']}
# Content Security Policy (GitHub Pages cannot send headers, so it goes in a meta tag).
# Only the translate bootstrap is inline; it is allowed by hash. 127.0.0.1 is for the local emulators.
def translate_init(lang):
 return f"function googleTranslateElementInit(){{new google.translate.TranslateElement({{pageLanguage:'{lang}',includedLanguages:'{INCLUDED_LANGS}',layout:google.translate.TranslateElement.InlineLayout.SIMPLE,autoDisplay:false}},'google_translate_element')}}"
# Google Translate runs one inline script inside an about:srcdoc frame. If Google changes it, translation
# stops and the browser console prints the new 'sha256-...' value to put here.
TRANSLATE_SRCDOC_HASH="'sha256-R6kjt5FwTd5vAw94Q08NLDZsSaGTzg4NsdIfKtECSp0='"
def csp(inline_scripts=()):
 hashes=' '.join(["'sha256-"+base64.b64encode(hashlib.sha256(x.encode()).digest()).decode()+"'" for x in inline_scripts]+([TRANSLATE_SRCDOC_HASH] if inline_scripts else []))
 return ("default-src 'self'; "
  f"script-src 'self' {hashes} https://www.gstatic.com https://apis.google.com https://translate.google.com https://translate.googleapis.com https://translate-pa.googleapis.com; "
  "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://www.gstatic.com https://translate.googleapis.com; "
  "font-src 'self' https://fonts.gstatic.com; "
  "img-src 'self' data: https:; "
  "connect-src 'self' https://*.googleapis.com https://script.google.com https://script.googleusercontent.com http://127.0.0.1:9099 http://127.0.0.1:8080; "
  "frame-src 'self' https://antarodaya-in.firebaseapp.com https://accounts.google.com https://translate.google.com; "
  "manifest-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'").replace('  ',' ')
def rupees(n):
 return '₹'+f'{n:,}'
for lang,n in [('hi',0),('en',1)]:
 def t(key): return texts[key][n]
 brand=BRAND[n]
 home=FILES['home'][n]
 site_data={'lang':lang,'homeUrl':home,'accountUrl':FILES['account'][n],'privacyUrl':FILES['privacy'][n],'adminUrl':FILES['admin'][n],'instagramUrl':config['instagramUrl'],'formUrl':form,
  'services':[{'id':s[0],'title':s[3][n],'options':[{'name':o[n],'fee':o[2]} for o in s[5]]} for s in services],'bookingNotifyUrl':config.get('bookingNotifyUrl',''),
  # Bookings store the option name in the customer's language; the admin looks fees up in either.
  'fees':{s[0]:{name:o[2] for o in s[5] for name in o[:2]} for s in services}}
 site_json=json.dumps(site_data,ensure_ascii=False).replace('</','<\\/')
 def header(kind):
  prefix='' if kind=='home' else home
  nav=''.join(f'<a href="{prefix}#{id}">{label}</a>' for id,label in zip(['services','rashi','how','about','reviews','contact'],t('nav')))
  hi_file,en_file=FILES[kind]
  translate=f'<details class="more-langs"><summary aria-label="{t("langTitle")}" title="{t("langTitle")}">{GLOBE_ICON}</summary><div class="lang-pop"><strong>{t("langTitle")}</strong><div id="google_translate_element" class="google-translate-widget"></div><small>{t("langText")}</small></div></details>' if kind=='home' else ''
  return f'''<header class="site-header"><div class="container header-inner"><div class="brand-wrap"><a href="{prefix}#home" class="brand" aria-label="{brand}"><img class="brand-logo" src="assets/brand/logo-mark.svg" width="52" height="52" alt=""><span><strong>{brand}</strong><small>{t('brand')}</small></span></a><details class="brand-meaning"><summary title="{t('meaningLabel')}"><span aria-hidden="true">✦</span><span class="sr-only">{t('meaningLabel')}</span></summary><div class="meaning-pop"><img src="assets/brand/logo-mark.svg" width="56" height="56" alt=""><strong>{t('meaningLabel')}</strong>{''.join(f'<p>{x}</p>' for x in t('meaning'))}<a class="text-link" href="{prefix}#services">{t('explore')}</a></div></details></div><nav aria-label="{'मुख्य नेविगेशन' if n==0 else 'Main navigation'}">{nav}</nav><div class="header-tools"><div class="lang-switch" role="group" aria-label="Language / भाषा"><a href="{hi_file}" lang="hi" hreflang="hi" {'aria-current="page"' if n==0 else ''}>हिं<span class="sr-only">दी</span></a><a href="{en_file}" lang="en" hreflang="en" {'aria-current="page"' if n==1 else ''}>EN</a></div>{translate}<div class="account-wrap"><a class="account-btn" href="{FILES['account'][n]}" data-account-button>{USER_ICON}<span class="account-label">{t('login')}</span></a></div></div></div></header>'''
 footer=f'''<footer><div class="container footer-inner"><div class="brand"><img class="brand-logo" src="assets/brand/logo-mark.svg" width="44" height="44" alt=""><span><strong>{brand}</strong><small>{t('footer')}</small></span></div><nav class="footer-links" aria-label="Footer"><a href="{home}#services">{t('nav')[0]}</a><a href="{home}#rashi">{t('nav')[1]}</a><a href="{home}#reviews">{t('nav')[4]}</a><a href="{FILES['account'][n]}">{t('accountTitle')}</a><a href="{FILES['privacy'][n]}">{t('privacyTitle')}</a><a href="{config['instagramUrl']}" target="_blank" rel="noopener noreferrer">Instagram</a></nav><div class="footer-connect"><strong>{t('connect')}</strong>{contact_links()}<small>{t('hours')}: {t('hoursText')}</small></div><p>© <span id="year">2026</span> {brand} · antarodaya.in</p></div></footer>'''
 def head(kind,title,desc,extra='',inline=()):
  hi_file,en_file=FILES[kind]
  me=FILES[kind][n]
  url=BASE+('' if me=='index.html' else me)
  robots='<meta name="robots" content="noindex,nofollow">' if kind in ('account','admin') else ''
  return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="{csp(inline)}"><meta name="referrer" content="strict-origin-when-cross-origin"><meta name="theme-color" content="#183d35"><title>{title}</title><meta name="description" content="{e(desc)}">{robots}<link rel="canonical" href="{url}"><link rel="alternate" hreflang="hi" href="{BASE+('' if hi_file=='index.html' else hi_file)}"><link rel="alternate" hreflang="en" href="{BASE+en_file}"><link rel="alternate" hreflang="x-default" href="{BASE+('' if en_file=='index.html' else en_file)}"><meta property="og:site_name" content="Antarodaya | अंतरोदय"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><meta property="og:locale" content="{'hi_IN' if n==0 else 'en_IN'}"><meta property="og:image" content="{BASE}assets/brand/og-image.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:url" content="{url}"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="icon" href="assets/brand/icon-192.png" type="image/png" sizes="192x192"><link rel="apple-touch-icon" href="assets/brand/apple-touch-icon.png"><link rel="manifest" href="manifest.webmanifest"><link rel="stylesheet" href="style.css"><script src="app.js" defer></script><script type="module" src="assets/js/main.js"></script>{extra}</head>'''
 # ---- Home page ----
 cards=''
 for id,num,icon,title,desc,options,prep,inc,proc,benefits in services:
  benefit_items=''.join(f'<li>{b}</li>' for b in benefits[n])
  fees=[o[2] for o in options]
  # data-fee lets assets/js/offer-ui.js show the month-end offer price next to the regular fee.
  option_rows=''.join(f'<li><span>{o[n]}</span><b data-fee="{o[2]}">{rupees(o[2])}</b></li>' for o in options)
  option_detail=''.join(f'<li><strong>{o[n]} · <span data-fee="{o[2]}">{rupees(o[2])}</span></strong><span>{o[3+n]}</span></li>' for o in options)
  cards+=f'''<article class="service-card" id="{id}"><div class="card-top"><span class="service-symbol" aria-hidden="true">{icon}</span><span class="serial">{num}</span></div><h3>{title[n]}</h3><p>{desc[n]}</p><div class="fee"><span data-fee="{min(fees)}">{rupees(min(fees))}</span> <small>{t('from')}</small></div><h4 class="options-title">{t('options')}</h4><ul class="option-list">{option_rows}</ul><p class="fee-note">{t('feeNote')}</p><details><summary>{t('details')}<span aria-hidden="true">{PLUS_ICON}</span></summary><div class="service-detail"><h4>{t('optionsDetail')}</h4><ul class="option-detail">{option_detail}</ul><h4>{t('benefitsHeading')}</h4><ul class="benefit-list">{benefit_items}</ul><h4>{t('prepare')}</h4><p>{prep[n]}</p><h4>{t('include')}</h4><p>{inc[n]}</p><h4>{t('process')}</h4><p>{proc[n]}</p><p class="small-note">{t('commonShort')} <a href="#notice">{t('noticeLink')}</a></p><a class="text-link" href="#contact">{t('choose')}</a></div></details></article>'''
 rashi_cards=''.join(f'''<article class="rashi-card"><span class="rashi-glyph" aria-hidden="true">{r[0]}</span><h3>{r[1+n]}<small>{r[2] if n==0 else r[1]}</small></h3><p class="rashi-meta">{t('rashiLord')}: {r[3+n]} · {r[5+n]}</p><p class="rashi-mantra" lang="sa"><span>{t('rashiMantra')}:</span> {r[7]}</p><p>{r[8+n]}</p></article>''' for r in rashis)
 steps=''.join(f'<article><span class="step-num">0{i+1}</span><h3>{a}</h3><p>{b}</p></article>' for i,(a,b) in enumerate(t('steps')))
 faqs=''.join(f'<details><summary>{q}<span aria-hidden="true">{PLUS_ICON}</span></summary><p>{a}</p></details>' for q,a in t('faqs'))
 formcta=f'<a class="button primary" href="{e(form)}" target="_blank" rel="noopener noreferrer">{t("formButton")}</a>' if form else f'<a class="button outline" href="{config["instagramUrl"]}" target="_blank" rel="noopener noreferrer">{t("instaButton")}</a>'
 bars=''.join(f'<li data-bar="{i}"><button type="button" class="bar-row" aria-pressed="false" disabled><span>{i}★</span><span class="bar"><i></i></span><output>0</output></button></li>' for i in range(5,0,-1))
 page_url=BASE+('' if home=='index.html' else home)
 ld={'@context':'https://schema.org','@graph':[
  {'@type':'Organization','@id':BASE+'#org','name':'Antarodaya','alternateName':'अंतरोदय','url':BASE,'logo':BASE+'assets/brand/icon-512.png','image':BASE+'assets/brand/og-image.png','description':t('metaDesc'),'sameAs':[config['instagramUrl'].split('?')[0],CONTACT.get('facebook','')],'areaServed':{'@type':'Country','name':'India'},'knowsLanguage':['hi','en']},
  {'@type':'WebSite','@id':BASE+'#website','url':BASE,'name':'Antarodaya','alternateName':'अंतरोदय','inLanguage':['hi','en'],'publisher':{'@id':BASE+'#org'}},
  {'@type':'WebPage','@id':page_url+'#page','url':page_url,'name':t('metaTitle'),'description':t('metaDesc'),'inLanguage':lang,'isPartOf':{'@id':BASE+'#website'},'about':{'@id':BASE+'#org'}},
  *[{'@type':'Service','@id':page_url+'#'+sv[0],'name':sv[3][n],'description':sv[4][n],'serviceType':'Astrology consultation','provider':{'@id':BASE+'#org'},'areaServed':{'@type':'Country','name':'India'},
     'offers':{'@type':'AggregateOffer','priceCurrency':'INR','lowPrice':min(o[2] for o in sv[5]),'highPrice':max(o[2] for o in sv[5]),'offerCount':len(sv[5])},
     'hasOfferCatalog':{'@type':'OfferCatalog','name':sv[3][n],'itemListElement':[{'@type':'Offer','name':o[n],'description':o[3+n],'price':o[2],'priceCurrency':'INR','url':page_url+'#'+sv[0]} for o in sv[5]]}} for sv in services],
  {'@type':'FAQPage','@id':page_url+'#faq','inLanguage':lang,'mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in t('faqs')]}]}
 ld_json=json.dumps(ld,ensure_ascii=False).replace('</','<\\/')
 html=head('home',t('metaTitle'),t('metaDesc'),f'<script type="application/ld+json">{ld_json}</script>',inline=(translate_init(lang),))+f'''
<body data-page="home"><a class="skip-link" href="#main">{t('skip')}</a>{header('home')}
<main id="main"><section class="hero container" id="home"><div class="hero-copy"><p class="eyebrow">{t('eyebrow')}</p><h1>{t('hero')}</h1><p class="hero-description">{t('desc')}</p><div class="hero-actions"><a class="button primary" href="#booking">{t('book')} <span aria-hidden="true">↗</span></a><a class="text-link" href="#services">{t('explore')}</a></div><p class="hero-note"><span aria-hidden="true">✧</span> {t('heroNote')}</p></div><div class="hero-art"><img src="assets/hero-illustration.svg" width="1536" height="1024" fetchpriority="high" alt="{'दीपक, रुद्राक्ष और पारंपरिक कुंडली की प्रतीकात्मक सज्जा' if n==0 else 'A symbolic arrangement of a diya, prayer beads and a traditional birth chart'}"><div class="image-caption"><img src="assets/brand/logo-mark.svg" width="34" height="34" alt=""><div><strong>{'ज्ञान · आस्था · चिंतन' if n==0 else 'Wisdom · Faith · Reflection'}</strong><small>ANTARODAYA</small></div></div></div></section>
<div class="values-strip"><div class="container"><span>✧ {'पारंपरिक दृष्टिकोण' if n==0 else 'Traditional perspectives'}</span><span>✧ {'स्पष्ट सेवा विवरण' if n==0 else 'Clear service details'}</span><span>✧ {'आपका निर्णय, आपकी स्वतंत्रता' if n==0 else 'Your choice, your agency'}</span></div></div>
<section class="section container" id="services"><div class="section-heading"><p class="eyebrow">{t('serviceTag')}</p><h2>{t('servicesTitle')}</h2><p>{t('servicesIntro')}</p></div><div class="service-grid">{cards}<aside class="service-aside"><span aria-hidden="true">✺</span><h3>{'एक सवाल से<br>शुरुआत करें।' if n==0 else 'Start with<br>one question.'}</h3><p>{'सेवा चुनने में उलझन है? पहले बात करके समझें कि कौन-सा परामर्श आपके लिए उपयुक्त है।' if n==0 else 'Not sure which service to choose? Get in touch to understand which consultation fits your question.'}</p><a href="#booking" class="button light">{t('book')} ↗</a></aside></div><a class="section-notice" href="#notice">ⓘ {t('commonShort')} <span>{t('noticeLink')} ↗</span></a></section>
<section class="section container rashi" id="rashi"><div class="section-heading"><p class="eyebrow">{t('rashiTag')}</p><h2>{t('rashiTitle')}</h2><p>{t('rashiIntro')}</p></div><div class="rashi-grid">{rashi_cards}</div><div class="rashi-foot"><p class="small-note">{t('rashiNote')}</p><a class="button primary" href="#kundali">{t('rashiCta')} ↗</a></div></section>
<section class="how-section" id="how"><div class="container section"><div class="section-heading"><p class="eyebrow">{t('howTag')}</p><h2>{t('howTitle')}</h2></div><div class="steps">{steps}</div></div></section>
<section class="section container about" id="about"><figure><a href="{e(config['instagramUrl'])}" target="_blank" rel="noopener noreferrer" aria-label="{t('instaButton')}"><img src="assets/antarodaya-portrait.png" width="768" height="1203" loading="lazy" alt="{t('illustration')}"></a><figcaption><a class="button primary" href="{e(config['instagramUrl'])}" target="_blank" rel="noopener noreferrer">{t('instaButton')}</a></figcaption></figure><div><p class="eyebrow">{t('aboutTag')}</p><h2>{t('aboutTitle')}</h2><p>{t('aboutText')}</p><p>{t('aboutText2')}</p><a class="text-link" href="#notice">{t('noticeLink')} ↗</a></div></section>
<section class="container payment" id="payment"><div><p class="eyebrow">{t('paymentTag')}</p><h2>{t('paymentTitle')}</h2><p>{t('paymentText')}</p><p class="small-note">{t('paymentNote')}</p></div><a class="qr-card" href="qr.png" target="_blank" rel="noopener"><img src="qr.png" width="220" height="220" loading="lazy" alt="{'मौजूदा भुगतान QR कोड' if n==0 else 'Existing payment QR code'}"><span>{t('qr')}</span></a></section>
<section class="section container reviews" id="reviews"><div class="section-heading"><p class="eyebrow">{t('reviewsTag')}</p><h2>{t('reviewsTitle')}</h2><p>{t('reviewsIntro')}</p></div><div class="reviews-layout"><aside class="rating-summary" data-rating-summary><p class="eyebrow">{t('overall')}</p><div class="rating-big"><span data-avg>—</span><div data-avg-stars></div></div><small data-count></small><ul class="rating-bars">{bars}</ul><button type="button" class="button primary block" data-write-review>{t('writeReview')} <span aria-hidden="true">✎</span></button><p class="small-note">{t('moderationNote')}</p></aside><div class="review-list" data-review-list aria-live="polite"><p class="review-empty">{t('reviewsLoading')}</p><noscript><p class="review-empty">{t('noscript')}</p></noscript></div></div></section>
<section class="section container booking" id="booking"><div class="section-heading"><p class="eyebrow">{t('bookTag')}</p><h2>{t('bookTitle')}</h2><p>{t('bookIntro')}</p></div><div class="booking-panel" data-booking><p class="review-empty">{t('reviewsLoading')}</p><noscript><p class="review-empty">{t('noscript')}</p></noscript></div></section>
<section class="section container" id="contact"><div class="section-heading"><p class="eyebrow">{t('contactTag')}</p><h2>{t('contactTitle')}</h2><p>{t('contactText')}</p></div><div class="contact-grid"><article><span class="contact-number">01 / FORM</span><h3>{t('formTitle')}</h3><p>{t('formAvailable') if form else t('formUnavailable')}</p>{formcta}</article><article><span class="contact-number">02 / INSTAGRAM</span><h3>@antarodaya_spiritual</h3><p>{t('instaText')}</p><a class="button primary" href="{config['instagramUrl']}" target="_blank" rel="noopener noreferrer">{t('instaButton')}</a></article></div><div class="contact-connect"><strong>{t('connect')}</strong>{contact_links()}</div><p class="privacy-note">{t('privacy')}</p></section>
<section class="container faq"><h2>{t('faqTitle')}</h2><div>{faqs}</div></section>
<aside class="container notice" id="notice"><h2>ⓘ {t('noticeTitle')}</h2><p>{t('notice')}</p></aside></main>
{footer}
<script type="application/json" id="site-data">{site_json}</script>
<script>{translate_init(lang)}</script>
<script src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit" async></script>
</body></html>'''
 (ROOT/FILES['home'][n]).write_text(html.replace('><', '>\n<') + '\n')
 # ---- Account and admin pages: rendered by JavaScript after login ----
 for kind in ('account','admin'):
  title=f"{t(kind+'Title')} | {brand}"
  page=head(kind,title,t('metaDesc'))+f'''
<body data-page="{kind}"><a class="skip-link" href="#main">{t('skip')}</a>{header(kind)}
<main id="main" class="container app-page" data-app><p class="review-empty">{t('reviewsLoading')}</p><noscript><p class="review-empty">{t('noscript')}</p></noscript></main>
{footer}
<script type="application/json" id="site-data">{site_json}</script>
</body></html>'''
  (ROOT/FILES[kind][n]).write_text(page.replace('><', '>\n<') + '\n')
 sections=''.join(f'<section><h2>{h}</h2><p>{body}</p></section>' for h,body in privacy[n])
 page=head('privacy',f"{t('privacyTitle')} | {brand}",t('metaDesc'))+f'''
<body data-page="privacy"><a class="skip-link" href="#main">{t('skip')}</a>{header('privacy')}
<main id="main" class="container legal"><p class="eyebrow">{brand}</p><h1>{t('privacyTitle')}</h1><p class="small-note">{t('privacyUpdated')}: {PRIVACY_UPDATED[n]}</p>{sections}</main>
{footer}
<script type="application/json" id="site-data">{site_json}</script>
</body></html>'''
 (ROOT/FILES['privacy'][n]).write_text(page.replace('><', '>\n<') + '\n')
(ROOT/'sitemap.xml').write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
'''+''.join(f'''<url><loc>{BASE+loc}</loc><xhtml:link rel="alternate" hreflang="en" href="{BASE}"/><xhtml:link rel="alternate" hreflang="hi" href="{BASE}hi.html"/><xhtml:link rel="alternate" hreflang="x-default" href="{BASE}"/><changefreq>weekly</changefreq><priority>{pr}</priority></url>
''' for loc,pr in [('','1.0'),('hi.html','0.9'),('privacy.html','0.3'),('privacy-hi.html','0.3')])+'</urlset>\n')
# Old addresses from before English became the default: send visitors to the new pages.
for old,new in [('en.html','')]:
 (ROOT/old).write_text(f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex"><link rel="canonical" href="{BASE+new}"><meta http-equiv="refresh" content="0;url=./{new}"><title>Antarodaya</title></head><body><a href="./{new}">Antarodaya</a></body></html>\n')
print('Built home, account and admin pages (hi + en) with',len(services),'services; Google Form configured:',bool(form))
