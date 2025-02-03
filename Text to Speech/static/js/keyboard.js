document.addEventListener("DOMContentLoaded", function() {
    const languageSelect = document.getElementById("language");

    // Add event listener for the language change
    languageSelect.addEventListener("change", function() {
        console.log('Language changed');
        changeKeyboard();
    });

    // Initialize the virtual keyboard with the default language
    changeKeyboard();
});

const keyboardLayouts = {
    en: [
        ['1','2','3','4','5','6','7','7','8','9','0'],
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '.', ',', '?', '!'],
        ['Space', 'Backspace']
    ],
    es: [
        ['1','2','3','4','5','6','7','7','8','9','0'],
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '¿', '¡', '.', ','],
        ['Space', 'Backspace']
    ],
    fr: [
        ['1','2','3','4','5','6','7','7','8','9','0'],
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'É', 'È', '.', ','],
        ['Space', 'Backspace']
    ],
    ru: [
        ['1','2','3','4','5','6','7','7','8','9','0'],
        ['Й', 'Ц', 'У', 'К', 'Е', 'Н', 'Г', 'Ш', 'Щ', 'З'],
        ['Ф', 'Ы', 'В', 'А', 'П', 'Р', 'О', 'Л', 'Д'],
        ['Я', 'Ч', 'С', 'М', 'И', 'Т', 'Ь', 'Б', 'Ю'],
        ['Space', 'Backspace']
    ],
    ar: [
        ['1','2','3','4','5','6','7','7','8','9','0'],
        ['ض', 'ص', 'ث', 'ق', 'ف', 'غ', 'ع', 'ه', 'خ', 'ح'],
        ['ش', 'س', 'ي', 'ب', 'ل', 'ا', 'ت', 'ن', 'م'],
        ['ك', 'ط', 'ئ', 'و', 'ي', 'ز', 'ظ', 'إ', 'أ'],
        ['Space', 'Backspace']
    ],
    de: [
        ['1','2','3','4','5','6','7','7','8','9','0'],
        ['Q', 'W', 'E', 'R', 'T', 'Z', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Y', 'X', 'C', 'V', 'B', 'N', 'M', 'Ä', 'Ö', 'Ü'],
        ['Space', 'Backspace']
    ],
    gr: [
        ['1','2','3','4','5','6','7','7','8','9','0'],
        ['Α', 'Β', 'Γ', 'Δ', 'Ε', 'Ζ', 'Η', 'Θ', 'Ι', 'Κ'],
        ['Λ', 'Μ', 'Ν', 'Ξ', 'Ο', 'Π', 'Ρ', 'Σ', 'Τ'],
        ['Υ', 'Φ', 'Χ', 'Ψ', 'Ω', 'Σ', 'Ε', 'Σ'],  
        ['Space', 'Backspace']
    ]
};

// Function to change the keyboard layout based on language selection
function changeKeyboard() {
    const language = document.getElementById("language").value;
    const layout = keyboardLayouts[language];
    const keyboardContainer = document.getElementById("keyboard");
    keyboardContainer.innerHTML = ""; // Clear the existing keyboard

    // Create the new keyboard layout
    layout.forEach(row => {
        const rowDiv = document.createElement("div");
        row.forEach(key => {
            const keyButton = document.createElement("button");
            keyButton.textContent = key;
            keyButton.classList.add('key'); // Add 'key' class for styling
            keyButton.onclick = () => appendToText(key);
            rowDiv.appendChild(keyButton);
        });
        keyboardContainer.appendChild(rowDiv);
    });

    console.log(`Selected language: ${language}`);
    console.log(`Selected layout: ${layout}`);
}

// Function to append the clicked key to the text area
function appendToText(key) {
    const textArea = document.getElementById("text");
    if (key === "Space") {
        textArea.value += " ";
    } else if (key === "Backspace") {
        textArea.value = textArea.value.slice(0, -1);
    } else {
        textArea.value += key;
    }
}

// Function to trigger text-to-speech conversion
function convertToSpeech() {
    event.preventDefault();
    const text = document.getElementById("text").value;
    const language = document.getElementById("language").value;
    
    if (text) {
        // Send text and language to the backend to convert to speech
        $.post("/convert", { text: text, language: language }, function(response) {
            // Update the audio player with the generated speech
            $("#audio-output").html(response);
            document.getElementById("text").value = "";  // Clear the text area
            document.getElementById("language").selectedIndex = 0
        }).fail(function() {
            alert("Error generating speech.");
        });
    }
}

