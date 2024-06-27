const voice_start_btn = document.getElementById('voice-start');
const voice_stop_btn  = document.getElementById('voice-stop');
const send_btn        = document.getElementById('send');
const request_field   = document.getElementById('request');
let recognition;

//	function correct_text(text, language = 'ru') {
//	    const API_URL = 'https://languagetool.org/api/v2/check';
//		request_to_server(`${API_URL}?language=${language}&text=${encodeURIComponent(text)}`, 'GET', null, 'json', null)
//	    .then(data => {
//			if (data.matches && data.matches.length > 0) {
//				// Создаем исправленную версию текста, заменяя ошибки на предложенные исправления
//				let corrected_text = text;
//				data.matches.forEach(match => {
//					match.replacements.forEach(replacement => {
//						corrected_text = corrected_text.substring(0, match.offset) + replacement.value + corrected_text.substring(match.offset + match.length);
//					});
//				});
//				return corrected_text;
//			} else {
//				return text;
//			}
//	    })
//	    .catch(error => {
//	        console.error('Ошибка при отправке запроса на сервер:', error);
//			return text;
//	    });
//	}

voice_start_btn.addEventListener('click', () => {
	voice_start_btn.style.display = 'none';
	voice_stop_btn.style.display  = 'flex';
	request_field.value           = '';

    recognition                = new webkitSpeechRecognition();
    recognition.continuous     = true;
    recognition.interimResults = true;
    recognition.lang           = 'ru-RU';

    let recognized_text = "";

    recognition.onresult = (event) => {
    	let interim_transcript = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {
    		let transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                if (!transcript.endsWith('.')) {
                    transcript += '.';
                }
                recognized_text += transcript;
            } else {
                interim_transcript += transcript;
            }
        }

        request_field.value = recognized_text + interim_transcript;
    };

    recognition.start();
});

voice_stop_btn.addEventListener('click', () => {
	voice_start_btn.style.display = 'flex';
	voice_stop_btn.style.display  = 'none';

    recognition.stop();
});

request_field.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        send();
    }
});

send_btn.addEventListener('click', () => {
	send();
});

function send() {
	if (request_field.value == "") {
		return
	}

	const chat = document.getElementById('chat');

	request_to_server('/chat/send', 'POST', 'json', 'json', {
		scene:    chat.dataset.scene,
		question: request_field.value
	})
    .then(data => {
    	document.querySelector("chat h1").innerHTML = "Чат :: " + data.scene_name;
    	chat.dataset.scene                          = data.scene_name;
    	create_message(data.question, 'question');
    	create_message(data.answer, 'answer');
    	request_field.value = "";

    	scrollToBottom();
    })
    .catch(error => {
        console.error('Ошибка при отправке запроса на сервер:', error);
    });
}

function scrollToBottom() {
    document.getElementById("chat-field").scrollTop = document.getElementById("chat-field").scrollHeight;
}

function end_dialog() {

	document.getElementById('end-dialog').style.display                = 'none';

    request_to_server('/chat/finish', 'POST', 'json', 'json')
	.then(data => {
        if (data.isnf) {
            request_to_server('/chat/rating', 'POST', 'text', 'json', "NF");
        } else {
            document.getElementById('end-dialog-successfully').style.display   = 'inline-block';
            document.getElementById('end-dialog-unsuccessfully').style.display = 'inline-block';
        }
    }).catch(error => {
        console.error('Ошибка при заполнении логов:', error);
    });

	if (recognition) {
		voice_start_btn.style.display = 'block';
		voice_stop_btn.style.display  = 'none';
		recognition.stop();
	}
}

function rating_dialog(rating) {
	document.getElementById('end-dialog').style.display                = 'inline-block';
	document.getElementById('end-dialog-successfully').style.display   = 'none';
	document.getElementById('end-dialog-unsuccessfully').style.display = 'none';

	if (recognition) {
		voice_start_btn.style.display = 'block';
		voice_stop_btn.style.display  = 'none';
		recognition.stop();
	}

	request_to_server('/chat/rating', 'POST', 'text', 'json', rating)
    .then(data => {
    	document.querySelector("chat h1").innerHTML = "Чат :: " + data.scene_name;
    	chat.dataset.scene                              = data.scene_name;
        document.getElementById("chat-field").innerHTML = '';

    	create_message(data.message, 'answer');
    	request_field.value = ""
    })
    .catch(error => {
        console.error('Ошибка при отправке запроса на сервер:', error);
    });
}

function create_message(text, class_) {
	let message_container = document.createElement('div');
	message_container.classList.add('message-container');
	document.getElementById("chat-field").appendChild(message_container);

	let message = document.createElement('div');
	message.textContent = text;
	message.classList.add(class_);
	message_container.appendChild(message);
}