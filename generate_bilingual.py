import csv
import io

def translate_text(text):
    if not text or text.strip() == "" or text.strip().lower() == "field resting":
        return "ಜಮೀನಿಗೆ ವಿಶ್ರಾಂತಿ"
    
    # Mapping of common English fragments to Kannada
    mapping = {
        "Book Tractor & Labor": "ಟ್ರಾಕ್ಟರ್ ಮತ್ತು ಕಾರ್ಮಿಕರನ್ನು ಬುಕ್ ಮಾಡಿ",
        "Check Weather": "ಹವಾಮಾನವನ್ನು ಪರಿಶೀಲಿಸಿ",
        "Land prep & puddling": "ಭೂಮಿ ಸಿದ್ಧತೆ ಮತ್ತು ಹದಗೊಳಿಸುವಿಕೆ",
        "Green Manuring": "ಹಸಿರು ಗೊಬ್ಬರ ಬಳಕೆ",
        "Get small plants ready in trays or bed": "ಸಣ್ಣ ಸಸಿಗಳನ್ನು ಸಿದ್ಧಪಡಿಸಿಕೊಳ್ಳಿ (ಟ್ರೇ ಅಥವಾ ಮಡಿಗಳಲ್ಲಿ)",
        "Soil testing & compost application": "ಮಣ್ಣಿನ ಪರೀಕ್ಷೆ ಮತ್ತು ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಬಳಕೆ",
        "Care for Seedlings": "ಸಸಿಗಳ ಆರೈಕೆ ಮಾಡಿ",
        "Transplant (15-18d)": "15-18 ದಿನಗಳ ಸಸಿಗಳನ್ನು ನಾಟಿ ಮಾಡಿ",
        "Apply Basal Mixture (Urea+DAP+Potash)": "ನಾಟಿ ಸಮಯದಲ್ಲಿ ಯೂರಿಯಾ, ಡಿಎಪಿ ಮತ್ತು ಪೊಟ್ಯಾಶ್ ಮಿಶ್ರಣವನ್ನು ಹಾಕಿ",
        "Apply 8 kg/Acre Zinc": "ಎಕರೆಗೆ 8 ಕೆಜಿ ಜಿಂಕ್ ಸಲ್ಫೇಟ್ ಹಾಕಿ",
        "(for green leaves)": "(ಹಸಿರು ಎಲೆಗಳಿಗಾಗಿ)",
        "Give water after planting": "ನಾಟಿ ಮಾಡಿದ ನಂತರ ನೀರು ಕೊಡಿ",
        "Gaps/Weeding": "ಖಾಲಿ ಇರುವ ಜಾಗದಲ್ಲಿ ಗಿಡಗಳನ್ನು ತುಂಬಿ ಮತ್ತು ಕಳೆ ತೆಗೆಯಿರಿ",
        "Water Saving (Water only if soil is dry)": "ನೀರಿನ ಉಳಿತಾಯ (ಮಣ್ಣು ಒಣಗಿದ್ದರೆ ಮಾತ್ರ ನೀರು ಕೊಡಿ)",
        "Apply 25% N (tillering) split": "ಶೇ. 25 ರಷ್ಟು ಯೂರಿಯಾ ಗೊಬ್ಬರವನ್ನು (ಸಸಿ ಒಡೆಯುವ ಹಂತದಲ್ಲಿ) ಹಾಕಿ",
        "Pull out weeds": "ಕಳೆಗಳನ್ನು ಕಿತ್ತೆಸೆಯಿರಿ",
        "Spray early morning/evening only": "ಮುಂಜಾನೆ ಅಥವಾ ಸಂಜೆ ವೇಳೆ ಮಾತ್ರ ಸಿಂಪಡಿಸಿ",
        "Scout: BPH": "ಪರಿಶೀಲಿಸಿ: ಜಿಗಿ ಹುಳು",
        "Stem Borer": "ಕಾಂಡಕೊರಕ",
        "Check for eggs": "ಮೊಟ್ಟೆಗಳಿಗಾಗಿ ಪರಿಶೀಲಿಸಿ",
        "resistant to Gall Midge": "ಗಾಲ್ ಮಿಡ್ಜ್ (ಹಿಪ್ಪುಳ) ರೋಗ ನಿರೋಧಕ ಶಕ್ತಿ ಹೊಂದಿದೆ",
        "Water Saving (Keep soil moist but not flooded)": "ನೀರಿನ ಉಳಿತಾಯ (ಮಣ್ಣಿನಲ್ಲಿ ತೇವಾಂಶವಿರಲಿ ಆದರೆ ನೀರು ನಿಲ್ಲಿಸಬೇಡಿ)",
        "Book Thresher & Labor": "ಒಕ್ಕಣೆ ಯಂತ್ರ ಮತ್ತು ಕಾರ್ಮಿಕರನ್ನು ಬುಕ್ ಮಾಡಿ",
        "Remove water before harvest": "ಕೊಯ್ಲಿಗೆ 10 ದಿನ ಮೊದಲು ನೀರನ್ನು ಹೊರಹಾಕಿ",
        "Apply 25% N (Grain forming stage )": "ಶೇ. 25 ರಷ್ಟು ಯೂರಿಯಾ ಗೊಬ್ಬರವನ್ನು (ಹಾಲು ತುಂಬುವ ಹಂತದಲ್ಲಿ) ಹಾಕಿ",
        "Do not water near harvest time": "ಬೆಳೆ ಕೊಯ್ಲಿಗೆ ಬರುವ ಮೊದಲು ನೀರು ಕೊಡಬೇಡಿ",
        "Cut and collect the crop": "ಬೆಳೆಯನ್ನು ಕೊಯ್ಲು ಮಾಡಿ ಮತ್ತು ಸಂಗ್ರಹಿಸಿ",
        "Dry grain to 14% moisture": "ಧಾನ್ಯವನ್ನು ಶೇ. 14 ರಷ್ಟು ತೇವಾಂಶ ಬರುವವರೆಗೆ ಒಣಗಿಸಿ",
        "Air-tight Bags": "ಗಾಳಿಯಾಡದ ಚೀಲಗಳು",
        "Ready land and give lime to soil": "ಭೂಮಿಯನ್ನು ಸಿದ್ಧಪಡಿಸಿ ಮತ್ತು ಮಣ್ಣಿಗೆ ಸುಣ್ಣ ಅಥವಾ ಡೋಲೊಮೈಟ್ ಹಾಕಿ",
        "Apply 4 kg/Acre Borax": "ಎಕರೆಗೆ 4 ಕೆಜಿ ಬೊರಾಕ್ಸ್ ಹಾಕಿ",
        "(for pod filling)": "(ಕಾಯಿ ತುಂಬುವಿಕೆಗಾಗಿ)",
        "Make soft bed for seeds": "ಬೀಜ ಬಿತ್ತಲು ಮಣ್ಣನ್ನು ಹದ ಮಾಡಿ",
        "Give small amount of water": "ಅಲ್ಪ ಪ್ರಮಾಣದ ನೀರು ಕೊಡಿ",
        "Sow (10\"x4\")": "10x4 ಇಂಚು ಅಂತರದಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಿ",
        "Apply 125 kg/Acre Gypsum powder": "ಎಕರೆಗೆ 125 ಕೆಜಿ ಜಿಪ್ಸಮ್ ಪುಡಿಯನ್ನು ಹಾಕಿ",
        "(for pod health)": "(ಕಾಯಿಗಳ ಆರೋಗ್ಯಕ್ಕಾಗಿ)",
        "half of 250kg/Acre total": "(ಒಟ್ಟು 250 ಕೆಜಿ ಜಿಪ್ಸಮ್‌ನಲ್ಲಿ ಅರ್ಧದಷ್ಟು)",
        "Apply 25 kg N First Dose and full dose of P & K at sowing": "ಬಿತ್ತನೆ ಸಮಯದಲ್ಲಿ 25 ಕೆಜಿ ಯೂರಿಯಾ ಮತ್ತು ಪೂರ್ಣ ಪ್ರಮಾಣದ ಡಿಎಪಿ/ಪೊಟ್ಯಾಶ್ ಹಾಕಿ",
        "Treat with PSB & Azospirillum": "ಪಿಎಸ್ಬಿ ಮತ್ತು ಅಜೋಸ್ಪೈರಿಲಮ್ ಜೈವಿಕ ಗೊಬ್ಬರದೊಂದಿಗೆ ಬೀಜೋಪಚಾರ ಮಾಡಿ",
        "Water when plants start to grow": "ಗಿಡಗಳು ಬೆಳೆಯಲು ಪ್ರಾರಂಭಿಸಿದಾಗ ನೀರು ಕೊಡಿ",
        "Remove weeds first time": "ಮೊದಲ ಬಾರಿ ಕಳೆ ತೆಗೆಯಿರಿ",
        "Monitor moisture": "ತೇವಾಂಶವನ್ನು ಗಮನಿಸಿ",
        "(30 DAS)": "(ಬಿತ್ತನೆ ಮಾಡಿದ 30 ದಿನಗಳ ನಂತರ)",
        "Scout: Tikka leaf spot and Rust": "ಪರಿಶೀಲಿಸಿ: ತಿಕ್ಕಾ ಎಲೆಚುಕ್ಕೆ ಮತ್ತು ತುಕ್ಕು ರೋಗ",
        "Pull out weeds again": "ಮತ್ತೊಮ್ಮೆ ಕಳೆ ಕಿತ್ತೆಸೆಯಿರಿ",
        "Critical moisture: ensure moisture for peg penetration": "ನಿರ್ಣಾಯಕ ಹಂತ: ಕಾಯಿಗಳು ಮಣ್ಣಿನಲ್ಲಿ ಇಳಿಯಲು ತೇವಾಂಶವಿರುವಂತೆ ನೋಡಿಕೊಳ್ಳಿ",
        "Flowering / pegging period": "ಹೂವಾಡುವ ಮತ್ತು ಕಾಯಿ ಕಟ್ಟುವ ಹಂತ",
        "Apply 10 kg Urea for Growth": "ಗಿಡದ ಬೆಳವಣಿಗೆಗಾಗಿ 10 ಕೆಜಿ ಯೂರಿಯಾ ಹಾಕಿ",
        "DO NOT allow soil to dry now": "ಈ ಸಮಯದಲ್ಲಿ ಮಣ್ಣು ಒಣಗಲು ಬಿಡಬೇಡಿ",
        "Mature pods or seeds forming": "ಕಾಯಿಗಳು ಅಥವಾ ಬೀಜಗಳು ಮಾಗುವ ಹಂತ",
        "Fungicide/insecticide spray": "ಶಿಲೀಂಧ್ರನಾಶಕ ಅಥವಾ ಕೀಟನಾಶಕ ಸಿಂಪಡಿಸಿ",
        "Inspect field before cutting": "ಕೊಯ್ಲಿಗೆ ಮೊದಲು ಜಮೀನನ್ನು ಪರೀಕ್ಷಿಸಿ",
        "Dry pods to 7-8% moisture": "ಕಾಯಿಗಳನ್ನು ಶೇ. 7-8 ತೇವಾಂಶ ಬರುವವರೆಗೆ ಒಣಗಿಸಿ",
        "prevent Aflatoxin": "ಅಫಲಾಟಾಕ್ಸಿನ್ (ಬೂಷ್ಟು) ಬರದಂತೆ ತಡೆಯಲು",
        "Scout: Aphids, Pod Borer": "ಪರಿಶೀಲಿಸಿ: ಹೇನು ಮತ್ತು ಕಾಯಿ ಕೊರಕ",
        "Apply before weeds come out Pendimethalin": "ಕಳೆ ಬರುವ ಮೊದಲು ಪೆಂಡಿಮೆಥಾಲಿನ್ ಬಳಸಿ",
        "Apply 50% N and full dose of P & K": "ಶೇ. 50 ರಷ್ಟು ಯೂರಿಯಾ ಮತ್ತು ಪೂರ್ಣ ಪ್ರಮಾಣದ ಡಿಎಪಿ/ಪೊಟ್ಯಾಶ್ ಹಾಕಿ",
        "Sowing pulses or peanuts": "ಬೇಳೆಕಾಳು ಅಥವಾ ಶೇಂಗಾ ಬಿತ್ತನೆ ಮಾಡಿ",
        "Spray 1% Urea": "ಶೇ. 1 ರಷ್ಟು ಯೂರಿಯಾ ದ್ರಾವಣವನ್ನು ಸಿಂಪಡಿಸಿ",
        "Check pod maturation": "ಕಾಯಿ ಬಲಿತಿರುವುದನ್ನು ಪರೀಕ್ಷಿಸಿ",
        "Harvest when 80% pods turn black": "ಶೇ. 80 ರಷ್ಟು ಕಾಯಿಗಳು ಕಪ್ಪಾದಾಗ ಕೊಯ್ಲು ಮಾಡಿ",
        "Store with Azadirachtin": "ಅಜಾಡಿರಾಕ್ಟಿನ್‌ನೊಂದಿಗೆ ಸಂಗ್ರಹಿಸಿ",
        "Prepare land and test soil and apply compost": "ಭೂಮಿ ಸಿದ್ಧಪಡಿಸಿ, ಮಣ್ಣು ಪರೀಕ್ಷೆ ಮಾಡಿ ಮತ್ತು ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಬಳಸಿ",
        "Sow seeds in trays or beds": "ಟ್ರೇ ಅಥವಾ ಮಡಿಗಳಲ್ಲಿ ಬೀಜ ಬಿತ್ತಿ",
        "Water and care for seedlings": "ಸಸಿಗಳಿಗೆ ನೀರು ಕೊಡಿ ಮತ್ತು ಆರೈಕೆ ಮಾಡಿ",
        "Remove weak seedlings": "ಬಲಹೀನ ಸಸಿಗಳನ್ನು ತೆಗೆಯಿರಿ",
        "Move 15–18 day-old seedlings to main field": "15-18 ದಿನಗಳ ಸಸಿಗಳನ್ನು ಮುಖ್ಯ ಜಮೀನಿಗೆ ವರ್ಗಾಯಿಸಿ",
        "Remove unwanted plants and replace missing ones": "ಅನಗತ್ಯ ಗಿಡಗಳನ್ನು ತೆಗೆದು ಖಾಲಿ ಇರುವ ಜಾಗದಲ್ಲಿ ಹೊಸ ಸಸಿಗಳನ್ನು ನಾಟಿ ಮಾಡಿ",
        "Scout: Blast leaf spots": "ಪರಿಶೀಲಿಸಿ: ಬೆಂಕಿರೋಗದ ಚುಕ್ಕೆಗಳು",
        "Blast (Prioritize Blast-tolerant varieties like KMP-220)": "ಬೆಂಕಿರೋಗ (ಕೆಎಂಪಿ-220 ನಂತಹ ರೋಗ ನಿರೋಧಕ ತಳಿಗಳಿಗೆ ಆದ್ಯತೆ ನೀಡಿ)",
        "Check if grains are forming": "ಧಾನ್ಯಗಳು ತುಂಬುತ್ತಿವೆಯೇ ಎಂದು ಪರೀಕ್ಷಿಸಿ",
        "Spray Tricyclazole for Blast": "ಬೆಂಕಿರೋಗಕ್ಕಾಗಿ ಟ್ರೈಸೈಕ್ಲಜೋಲ್ ಸಿಂಪಡಿಸಿ",
        "Chlorantraniliprole for Stem Borer": "ಕಾಂಡಕೊರಕ ನಿಯಂತ್ರಣಕ್ಕೆ ಕ್ಲೋರಾಂಟ್ರಾನಿಲಿಪ್ರೋಲ್ ಬಳಸಿ",
        "Reduce water and stop watering before harvest": "ಕೊಯ್ಲಿಗೆ ಮೊದಲು ನೀರಿನ ಪ್ರಮಾಣ ಕಡಿಮೆ ಮಾಡಿ ಮತ್ತು ನಂತರ ನಿಲ್ಲಿಸಿ",
        "Collect and store rice and remove straw": "ಭಕ್ಕಿ ಸಂಗ್ರಹಿಸಿ ಮತ್ತು ಒಣ ಹುಲ್ಲನ್ನು ತೆಗೆಯಿರಿ",
        "Clean and repair field": "ಜಮೀನನ್ನು ಸ್ವಚ್ಛಗೊಳಿಸಿ ಮತ್ತು ಬದುಗಳನ್ನು ಸರಿಪಡಿಸಿ",
        "Spray Tebuconazole 2DS or Mancozeb for leaf spots": "ಎಲೆಚುಕ್ಕೆ ರೋಗಕ್ಕೆ ಟೆಬುಕೊನಜೋಲ್ ಅಥವಾ ಮ್ಯಾಂಕೋಜೋಬ್ ಸಿಂಪಡಿಸಿ",
        "Drain water before harvest": "ಕೊಯ್ಲಿಗೆ ಮೊದಲು ನೀರನ್ನು ಹೊರಹಾಕಿ",
        "Clean and level the land for planting": "ನಾಟಿಗಾಗಿ ಜಮೀನನ್ನು ಸ್ವಚ್ಛಗೊಳಿಸಿ ಮತ್ತು ಸಮತಟ್ಟು ಮಾಡಿ",
        "Apply Fertilizer kg/ha (50% Nitrogen First Dose, full P&K)": "ಬಿತ್ತನೆ ಸಮಯದಲ್ಲಿ ಶೇ. 50 ಯೂರಿಯಾ ಮತ್ತು ಪೂರ್ಣ ಡಿಎಪಿ/ಪೊಟ್ಯಾಶ್ ಹಾಕಿ",
        "Mark planting rows / Prepare irrigation": "ಸಾಲುಗಳನ್ನು ಗುರುತಿಸಿ ಮತ್ತು ನೀರಾವರಿ ಸಿದ್ಧತೆ ಮಾಡಿ",
        "Field layout: 1.5 m between channels and 0.6 m between hills": "ವಿನ್ಯಾಸ: ಕಾಲುವೆಗಳ ನಡುವೆ 1.5 ಮೀಟರ್ ಮತ್ತು ಗುಂಡಿಗಳ ನಡುವೆ 0.6 ಮೀಟರ್ ಅಂತರವಿರಲಿ",
        "Apply 25% Urea for Growth": "ಗಿಡದ ಬೆಳವಣಿಗೆಗಾಗಿ ಶೇ. 25 ರಷ್ಟು ಯೂರಿಯಾ ಹಾಕಿ",
        "Apply final 25% Urea for Growth (45 DAS)": "45 ನೇ ದಿನದಲ್ಲಿ ಉಳಿದ ಶೇ. 25 ರಷ್ಟು ಯೂರಿಯಾ ಹಾಕಿ",
        "Monitor plant health": "ಗಿಡದ ಆರೋಗ್ಯವನ್ನು ಗಮನಿಸಿ",
        "Scout: Fruit Fly": "ಪರಿಶೀಲಿಸಿ: ಹಣ್ಣಿನ ನೊಣ",
        "Pheromone/Fish meal traps": "ಫೆರೋಮೋನ್ ಅಥವಾ ಮೀನಿನ ಪುಡಿ ಬಲೆಗಳನ್ನು ಬಳಸಿ",
        "2% neem oil + garlic emulsion for sucking pests": "ಹೀರುವ ಕೀಟಗಳಿಗಾಗಿ ಶೇ. 2 ರಷ್ಟು ಬೇವಿನ ಎಣ್ಣೆ ಮತ್ತು ಬೆಳ್ಳುಳ್ಳಿ ಕಷಾಯ ಬಳಸಿ",
        "judge harvest readiness": "ಕೊಯ್ಲಿಗೆ ಸಿದ್ಧತೆಯನ್ನು ಪರೀಕ್ಷಿಸಿ",
        "dull sound when thumping the fruit": "ಹಣ್ಣನ್ನು ತಟ್ಟಿದಾಗ ಮಂದವಾದ ಶಬ್ದ ಬಂದರೆ ಕೊಯ್ಲಿಗೆ ಸಿದ್ಧ",
        "Apply 50% Nitrogen and full Phosphorus/Potassium as First Dose": "ಬಿತ್ತನೆ ಸಮಯದಲ್ಲಿ ಶೇ. 50 ಯೂರಿಯಾ ಮತ್ತು ಪೂರ್ಣ ಡಿಎಪಿ/ಪೊಟ್ಯಾಶ್ ಹಾಕಿ",
        "spacing": "ಅಂತರ",
        "Prepare seedbed": "ಬಿತ್ತನೆ ಮಡಿ ಸಿದ್ಧಪಡಿಸಿ",
        "Sow seeds 12 inches apart in rows, with 4 inches between seeds": "ಸಾಲುಗಳ ನಡುವೆ 12 ಇಂಚು ಮತ್ತು ಬೀಜಗಳ ನಡುವೆ 4 ಇಂಚು ಅಂತರವಿರಲಿ",
        "Irrigate lightly": "ಹಗುರವಾಗಿ ನೀರು ಕೊಡಿ",
        "Weed at 20-25 days after sowing": "ಬಿತ್ತನೆ ಮಾಡಿದ 20-25 ದಿನಗಳ ನಂತರ ಕಳೆ ತೆಗೆಯಿರಿ",
        "yellow mosaic and thrips": "ಹಳದಿ ಎಲೆ ರೋಗ ಮತ್ತು ನುಸಿ ಕೀಟ",
        "Harvest when 80% pods mature": "ಶೇ. 80 ರಷ್ಟು ಕಾಯಿಗಳು ಮಾಗಿದಾಗ ಕೊಯ್ಲು ಮಾಡಿ",
        "Dry plants on tarpaulin": "ಗಿಡಗಳನ್ನು ಟಾರ್ಪಾಲಿನ್ ಮೇಲೆ ಒಣಗಿಸಿ",
        "Thin seedlings to one per hill": "ಪ್ರತಿ ಗುಂಡಿಯಲ್ಲಿ ಒಂದು ಸಸಿ ಮಾತ್ರ ಇರುವಂತೆ ಮಾಡಿ",
        "Thinning": "ಗಿಡಗಳ ವಿರಳೀಕರಣ",
        "leaf yellowing for maturation signals": "ಬೆಳೆ ಮಾಗುವ ಸೂಚನೆಯಾಗಿ ಎಲೆಗಳು ಹಳದಿ ಬಣ್ಣಕ್ಕೆ ತಿರುಗುವುದನ್ನು ಗಮನಿಸಿ",
        "Maintain exactly 5% moisture": "ತೈಲದ ಅಂಶ ಕೆಡದಂತೆ ನಿಖರವಾಗಿ ಶೇ. 5 ರಷ್ಟು ತೇವಾಂಶ ಕಾಪಾಡಿಕೊಳ್ಳಿ",
        "700-gauge poly bags": "700-ಗೇಜ್ ಪಾಲಿ ಬ್ಯಾಗ್ ಬಳಸಿ",
        "Clear crop residues": "ಬೆಳೆಯ ಕಸಕಡ್ಡಿಗಳನ್ನು ಸ್ವಚ್ಛಗೊಳಿಸಿ",
        "Apply 200kg/Acre Lime/Dolomite": "ಎಕರೆಗೆ 200 ಕೆಜಿ ಸುಣ್ಣ ಅಥವಾ ಡೋಲೊಮೈಟ್ ಹಾಕಿ",
        "Ensure proper drainage": "ನೀರನ್ನು ಹೊರಹೋಗಲು ಸರಿಯಾದ ವ್ಯವಸ್ಥೆ ಮಾಡಿ",
        "Near sea? Check water salinity": "ಸಮುದ್ರದ ಸಮೀಪವಿದ್ದರೆ ನೀರಿನ ಉಪ್ಪಿನಂಶ ಪರೀಕ್ಷಿಸಿ",
        "Panicle emergence monitoring": "ತೆನೆ ಬರುವ ಹಂತವನ್ನು ಗಮನಿಸಿ",
        "Maintain nursery irrigation": "ಸಸಿಮಡಿಗೆ ಸರಿಯಾಗಿ ನೀರು ಕೊಡಿ",
        "Apply 6 kg/Acre MgSO4": "ಎಕರೆಗೆ 6 ಕೆಜಿ ಮೆಗ್ನೀಸಿಯಮ್ ಸಲ್ಫೇಟ್ ಹಾಕಿ",
        "Scout: BSFB": "ಪರಿಶೀಲಿಸಿ: ಕಾಯಿ ಕೊರಕ",
        "Scout: Whitefly": "ಪರಿಶೀಲಿಸಿ: ಬಿಳಿ ನೊಣ",
        "YVMV vector": "ವೈವಿಎಂವಿ ವೈರಸ್ ಹರಡುವ ಕೀಟ",
        "Apply Imidacloprid for Whiteflies": "ಬಿಳಿ ನೊಣದ ನಿಯಂತ್ರಣಕ್ಕೆ ಇಮಿಡಾಕ್ಲೋಪ್ರಿಡ್ ಬಳಸಿ",
        "Harvest when fruit is shiny, firm and medium-sized": "ಹಣ್ಣು ಹೊಳೆಯುವಂತೆ, ಗಟ್ಟಿಯಾಗಿ ಮತ್ತು ಮಧ್ಯಮ ಗಾತ್ರದಲ್ಲಿದ್ದಾಗ ಕೊಯ್ಲು ಮಾಡಿ",
        "Kharif": "ಖಾರಿಫ್",
        "Rabi": "ಹಿಂಗಾರು (ರಬಿ)",
        "Summer": "ಬೇಸಿಗೆ",
        "Paddy": "ಭತ್ತ",
        "Groundnut": "ಶೇಂಗಾ",
        "Black gram": "ಉದ್ದು",
        "Green gram": "ಹೆಸರು ಬೇಳೆ",
        "Cowpea": "ಅಲಸಂದೆ",
        "Sesame": "ಎಳ್ಳು",
        "Vegetables": "ತರಕಾರಿಗಳು",
        "Cucumber": "ಸೌತೆಕಾಯಿ",
        "Watermelon": "ಕಲ್ಲಂಗಡಿ",
        "Brinjal": "ಬದನೆಕಾಯಿ",
        "Chilli": "ಮೆಣಸಿನಕಾಯಿ",
        "Lady's Finger": "ಬೆಂಡೆಕಾಯಿ",
        "June": "ಜೂನ್",
        "July": "ಜುಲೈ",
        "August": "ಆಗಸ್ಟ್",
        "September": "ಸೆಪ್ಟೆಂಬರ್",
        "October": "ಅಕ್ಟೋಬರ್",
        "November": "ನವೆಂಬರ್",
        "December": "ಡಿಸೆಂಬರ್",
        "January": "ಜನವರಿ",
        "February": "ಫೆಬ್ರವರಿ",
        "March": "ಮಾರ್ಚ್",
        "April": "ಏಪ್ರಿಲ್",
        "May": "ಮೇ"
    }
    
    parts = text.split("|")
    translated_parts = []
    
    for part in parts:
        clean_part = part.strip()
        translated_part = clean_part
        # Try to find replacements for key fragments within the text
        for eng, kn in mapping.items():
            if eng in translated_part:
                translated_part = translated_part.replace(eng, kn)
        
        # If nothing was translated and it's not a known symbol, 
        # keep it but it might need manual review
        translated_parts.append(translated_part)
        
    return " | ".join(translated_parts)

with open('calendar.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

output_rows = []
for row in rows:
    new_row = row.copy()
    new_row['Week 1 (KN)'] = translate_text(row['Week 1'])
    new_row['Week 2 (KN)'] = translate_text(row['Week 2'])
    new_row['Week 3 (KN)'] = translate_text(row['Week 3'])
    new_row['Week 4 (KN)'] = translate_text(row['Week 4'])
    output_rows.append(new_row)

fieldnames = reader.fieldnames + ['Week 1 (KN)', 'Week 2 (KN)', 'Week 3 (KN)', 'Week 4 (KN)']

with open('calendar_bilingual.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output_rows)

print("Bilingual CSV generated successfully!")
