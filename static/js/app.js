document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const speakButton = document.getElementById('speak-button');
    const userTextElement = document.getElementById('user-text');
    const assistantTextElement = document.getElementById('assistant-text');
    
    // MediaRecorder variables
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    
    // Initialize the application
    initApp();
    
    function initApp() {
        // Set up button click handler
        speakButton.addEventListener('click', toggleRecording);
        
        // Initialize button style
        speakButton.classList.add('btn-start');
    }
    
    async function toggleRecording() {
        if (!isRecording) {
            // Start recording
            startRecording();
        } else {
            // Stop recording
            stopRecording();
        }
    }
    
    async function startRecording() {
        try {
            // Request access to the microphone
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Clear only the user text, keep assistant text
            userTextElement.innerHTML = '';
            
            // Create media recorder
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            // Collect audio data
            mediaRecorder.addEventListener('dataavailable', event => {
                audioChunks.push(event.data);
            });
            
            // Start recording
            mediaRecorder.start();
            isRecording = true;
            
            // Update button text and style
            speakButton.textContent = 'Stop';
            speakButton.classList.remove('btn-start');
            speakButton.classList.add('btn-stop');
            
        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Error accessing microphone. Please ensure you have allowed microphone access.');
        }
    }
    
    function stopRecording() {
        if (!mediaRecorder) return;
        
        // Clear assistant text when stopping the recording
        assistantTextElement.innerHTML = '';
        
        // Update state and button text
        isRecording = false;
        speakButton.textContent = 'Processing...';
        speakButton.disabled = true;
        speakButton.classList.remove('btn-stop');
        speakButton.classList.add('btn-processing');
        
        // Stop recording
        mediaRecorder.addEventListener('stop', processAudio);
        mediaRecorder.stop();
        
        // Stop all microphone tracks
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
    
    async function processAudio() {
        try {
            // Create audio blob and convert to base64
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const reader = new FileReader();
            
            reader.onload = async function(event) {
                const audioBase64 = event.target.result;
                await processAudioInSteps(audioBase64);
            };
            
            reader.readAsDataURL(audioBlob);
            
        } catch (error) {
            console.error('Error processing audio:', error);
            resetButton();
        }
    }
    
    async function processAudioInSteps(audioData) {
        try {
            // Step 1: Get transcription first
            const transcriptionResponse = await fetch('/api/process-audio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ audio: audioData })
            });
            
            if (!transcriptionResponse.ok) {
                throw new Error('Server error during transcription');
            }
            
            const transcriptionData = await transcriptionResponse.json();
            
            // Display transcription with mispronounced words in red
            displayTranscription(transcriptionData.transcription, transcriptionData.wordsWithConfidence);
            
            // Step 2: Generate response
            const responseResponse = await fetch('/api/generate-response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(transcriptionData)
            });
            
            if (!responseResponse.ok) {
                throw new Error('Server error during response generation');
            }
            
            const responseData = await responseResponse.json();
            
            // Display assistant response
            displayAssistantResponse(responseData.response);
            
            // Reset button
            resetButton();
            
        } catch (error) {
            console.error('Error processing speech:', error);
            alert('Error processing your speech. Please try again.');
            resetButton();
        }
    }
    
    function resetButton() {
        speakButton.textContent = 'Speak';
        speakButton.disabled = false;
        speakButton.classList.remove('btn-stop', 'btn-processing');
        speakButton.classList.add('btn-start');
    }
    
    function displayTranscription(text, wordsWithConfidence) {
        if (!text) return;
        
        
        // Split the text into individual tokens (words and spacing)
        // This regex matches words while preserving punctuation separately
        const tokens = text.match(/[\w']+|[.,!?;:""''\-–—()]|\s+/g) || [];
        
        // Combine tokens to rebuild words with their surrounding punctuation
        const words = [];
        let currentWord = '';
        let wordIndex = 0;
        
        tokens.forEach(token => {
            if (/\s+/.test(token)) {
                // If we have a current word, push it to words array and reset
                if (currentWord) {
                    words.push({
                        word: currentWord,
                        index: wordIndex++
                    });
                    currentWord = '';
                }
                // Add space as a separate entry
                words.push({
                    word: token,
                    isSpace: true
                });
            } else if (/[.,!?;:""''\-–—()]/.test(token)) {
                // If it's punctuation, add it to current word if exists, otherwise treat as standalone
                if (currentWord) {
                    currentWord += token;
                } else {
                    words.push({
                        word: token,
                        isPunctuation: true
                    });
                }
            } else {
                // It's a regular word
                currentWord += token;
            }
        });
        
        // Add any remaining word
        if (currentWord) {
            words.push({
                word: currentWord,
                index: wordIndex++
            });
        }
        
        // Create a map of words to highlight
        const wordsToHighlight = {};
        wordsWithConfidence.forEach(wordInfo => {
            if (wordInfo.is_low_confidence) {
                wordsToHighlight[wordInfo.position] = wordInfo.word;
            }
        });
        
        // Create the display text with highlights
        const highlightedText = words.map(item => {
            if (item.isSpace) {
                return item.word; // Return spaces as is
            } else if (item.isPunctuation) {
                return item.word; // Return punctuation as is
            } else if (item.index in wordsToHighlight) {
                // Extract actual word part without punctuation
                const wordPart = item.word.match(/[\w']+/)[0];
                const beforePunctuation = item.word.split(wordPart)[0] || '';
                const afterPunctuation = item.word.split(wordPart)[1] || '';
                
                // Only highlight the word part, not the punctuation
                return beforePunctuation + 
                       `<span class="red-text">${wordPart}</span>` + 
                       afterPunctuation;
            }
            return item.word;
        }).join('');
        
        userTextElement.innerHTML = highlightedText;
    }
    
    function displayAssistantResponse(text) {
        if (text) {
            assistantTextElement.textContent = text;
        }
    }
}); 