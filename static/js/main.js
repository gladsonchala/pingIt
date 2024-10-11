document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("adminModal");
    const closeBtn = document.querySelector(".close");
    const deleteForm = document.getElementById("deleteForm");
    let botIndexToDelete = null;

    // Open Modal on Delete Click
    document.querySelectorAll('.delete-btn').forEach((btn, index) => {
        btn.addEventListener('click', function() {
            botIndexToDelete = this.getAttribute("data-id");
            document.getElementById("botIndex").value = botIndexToDelete;
            modal.style.display = "block";
        });
    });

    // Close Modal
    closeBtn.onclick = function() {
        modal.style.display = "none";
    };

    // Close Modal When Clicking Outside
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };

    // Submit Delete Form
    deleteForm.onsubmit = async function(e) {
        e.preventDefault();
        const adminPassword = document.getElementById("adminPassword").value;
        const botIndex = document.getElementById("botIndex").value;
        
        const response = await fetch(`/delete/${botIndex}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ password: adminPassword })
        });

        const result = await response.json();
        if (result.success) {
            window.location.reload(); // Reload the page to reflect the deletion
        } else {
            alert("Incorrect password!");
        }
    };
});
