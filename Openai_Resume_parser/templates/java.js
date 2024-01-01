<input type="file" id="resume" name="resume" required>
<a href="#" class="button" onclick="getInsights()">Get Insights</a>

<script>
    function getInsights() {
        var fileInput = document.getElementById('resume');
        var file = fileInput.files[0];

        var formData = new FormData();
        formData.append('resume', file);

        fetch('/get-insights', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Error:', error));
    }
</script>
