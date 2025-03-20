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
            
            // Display transcription with mispronounced words in red immediately
            displayTranscription(transcriptionData.transcription, transcriptionData.lowConfidenceWords);
            
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
    
    function displayTranscription(text, lowConfidenceWords) {
        if (!text) return;
        
        // If there are no low confidence words, just display the text
        if (!lowConfidenceWords || lowConfidenceWords.length === 0) {
            userTextElement.textContent = text;
            return;
        }
        
        // Otherwise, highlight the low confidence words in red
        let displayText = text;
        
        // Replace each low confidence word with a span with red color
        lowConfidenceWords.forEach(word => {
            const regex = new RegExp(`\\b${word}\\b`, 'gi');
            displayText = displayText.replace(regex, `<span class="red-text">${word}</span>`);
        });
        
        userTextElement.innerHTML = displayText;
    }
    
    function displayAssistantResponse(text) {
        if (text) {
            assistantTextElement.textContent = text;
        }
    }
}); 