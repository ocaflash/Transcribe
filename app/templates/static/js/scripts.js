document.getElementById('settings-form').addEventListener('submit', function(e) {
    e.preventDefault();

    var formData = new FormData(this);
    var xhr = new XMLHttpRequest();

    xhr.open('POST', '/api/v1/settings', true);

    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                alert('Settings saved successfully');
            } else {
                alert('Error saving settings: ' + xhr.statusText);
            }
        }
    };

    xhr.send(formData);
});

document.getElementById('upload-form').addEventListener('submit', function(e) {
    e.preventDefault();

    var formData = new FormData(this);
    var xhr = new XMLHttpRequest();

    xhr.open('POST', '/api/v1/upload', true);

    xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
            var percentComplete = (e.loaded / e.total) * 100;
            document.getElementById('upload-progress').style.width = percentComplete + '%';
        }
    };

    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                document.getElementById('status-messages').innerHTML += '<p>File uploaded and processed successfully.</p>';
            } else {
                document.getElementById('status-messages').innerHTML += '<p>Error: ' + xhr.statusText + '</p>';
            }
        }
    };

    document.getElementById('progress-container').style.display = 'block';
    xhr.send(formData);
});
