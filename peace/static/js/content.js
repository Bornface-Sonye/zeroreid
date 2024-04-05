document.addEventListener("DOMContentLoaded", function() {
    var button1 = document.getElementById("button1");
    var button2 = document.getElementById("button2");
    var rightDiv = document.getElementById("right");

    function loadContent(url) {
        fetch(url)
            .then(response => response.text())
            .then(data => {
                rightDiv.innerHTML = data;
            })
            .catch(error => console.error('Error fetching content:', error));
    }

    button1.addEventListener("click", function() {
        loadContent("{% url 'answer' %}");
    });

    button2.addEventListener("click", function() {
        loadContent("{% url 'report' %}");
    });
});