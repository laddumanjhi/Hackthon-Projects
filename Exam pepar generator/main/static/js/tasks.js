// tasks.js

// Function to handle task selection based on taskId
function selectTask(taskId) {
    let url = '';
    switch(taskId) {
        case 'generate_exam_questions':
            url = '/generate_exam_questions';
            break;
        case 'generate_exam_paper':
            url = '/generate_exam_paper';
            break;
        case 'get_syllabus':
            url = '/get_syllabus';
            break;
        case 'important_questions':
            url = '/important_questions';
            break;
        case 'study_package':
            url = '/generate_study_package';
            break;
        default:
            console.error('Unknown task ID:', taskId);
            return;
    }

    // Send a POST request
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})  // Send an empty JSON object or any required data
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Handle success response
            console.log(data);
        } else {
            // Handle error response
            console.error(data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to handle the click event for the task card
function handleClick(url) {
    console.log('Task card clicked');
    alert('Redirecting to: ' + url);
    window.location.href = url;
}
let card = document.querySelector("task-card")
// card.onlink = handleClick('{ url_for('generate_exam_questions')}');

document.getElementById('loginButton').addEventListener('click', async (e) => {
    e.preventDefault();
    document.getElementById('loadingSpinner').style.display = 'block'; // Show loading spinner
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        const data = await response.json();
        if (data.success) {
            window.location.href = '/dashboard';
        } else {
            alert(data.error);
        }
    } catch (error) {
        alert('An error occurred during login');
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none'; // Hide loading spinner
    }
});

// Assuming you have a function to fetch data
async function fetchData() {
    // Show loading spinner
    document.getElementById('loadingSpinner').style.display = 'block';

    try {
        // Simulate data fetching
        const response = await fetch('your-api-endpoint'); // Replace with your API endpoint
        const data = await response.json();
        
        // Process your data here
    } catch (error) {
        console.error('Error fetching data:', error);
    } finally {
        // Hide loading spinner
        document.getElementById('loadingSpinner').style.display = 'none';
    }
}

// Add event listener to the generate button
document.getElementById('generateBtn').addEventListener('click', fetchData);

document.getElementById('signupButton').addEventListener('click', async (e) => {
    e.preventDefault();
    const name = document.getElementById('name').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const educationLevel = document.getElementById('educationLevel').value;

    // Check for empty fields
    if (!name || !email || !password || !confirmPassword || !educationLevel) {
        alert("Please fill in all fields.");
        return;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return;
    }

    document.getElementById('loadingSpinner').style.display = 'block'; // Show loading spinner
    try {
        const response = await fetch('/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                email: email,
                password: password,
                education_level: educationLevel
            })
        });
        const data = await response.json();
        if (data.success) {
            window.location.href = '/dashboard';
        } else {
            alert(data.error || "Signup failed. Please try again.");
        }
    } catch (error) {
        alert('An error occurred during signup: ' + error.message);
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none'; // Hide loading spinner
    }
});

document.getElementById('guestLoginButton').addEventListener('click', async (e) => {
    e.preventDefault();
    const guestName = prompt("Please enter your name:");
    console.log("Guest Name Prompted:", guestName); // Log the guest name
    if (guestName) {
        console.log("Redirecting to dashboard with guest name:", guestName); // Log before redirect
        // Redirect to dashboard with guest name
        window.location.href = '/dashboard?guestName=' + encodeURIComponent(guestName);
    } else {
        alert("Name is required to log in as a guest.");
    }
});