function request_to_server(url, method, send_type, response_type, request_data) {
    return new Promise((resolve, reject) => {
        // Создаем XMLHttpRequest объект
        const xhr = new XMLHttpRequest();
        xhr.open(method, url);

        // Устанавливаем Content-Type и Accept в зависимости от типа отправки и получения данных
        if (send_type === 'json') {     xhr.setRequestHeader('Content-Type', 'application/json'); }
        if (response_type === 'json') { xhr.setRequestHeader('Accept',       'application/json'); }

        // Обрабатываем ответ от сервера
        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                let response;
                if (response_type === 'json') {
                    response = JSON.parse(xhr.responseText);
                } else {
                    response = xhr.responseText;
                }
                resolve(response);
            } else {
                reject(xhr.statusText);
            }
        };

        // Обработка ошибок запроса
        xhr.onerror = () => {
            reject(xhr.statusText);
        };

        // Отправляем данные на сервер
        if (send_type === 'json') {
            request_data = JSON.stringify(request_data);
        } else {
            request_data = request_data;
        }
        xhr.send(request_data);
    });
}