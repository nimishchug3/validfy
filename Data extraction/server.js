const express = require('express');
const multer = require('multer');
const upload = multer({ dest: 'uploads/' }); // Specify a destination for uploaded files
const axios = require('axios'); // Make sure to import axios
const fs = require('fs');
const FormData = require('form-data');
const { MongoClient } = require('mongodb'); // Import MongoDB client

const app = express();

// Middleware to parse JSON and URL-encoded data
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.set('view engine', 'ejs');
app.set('views', './public');
app.use(express.static('public'));

// MongoDB Connection URI
const uri = "YOUR_MOGODB_URI"; // Replace with your MongoDB URI
const client = new MongoClient(uri);

async function connectDB() {
    try {
        await client.connect();
        console.log("Connected to MongoDB");
    } catch (err) {
        console.error("Failed to connect to MongoDB", err);
    }
}

connectDB();

// Function to compare form data with API response
function matchData(formData, apiData) {
    const mismatches = [];

    // Compare Aadhaar number (remove any spaces or special characters from both)
    const formAadhar = formData.aadhar.replace(/\D/g, '');
    if (formAadhar !== apiData.AADHAR_NUMBER) {
        mismatches.push({ field: 'AADHAR_NUMBER', form: formAadhar, api: apiData.AADHAR_NUMBER });
    }

    // Compare first name and last name (case-insensitive)
    if (formData.firstName.toLowerCase() !== apiData["FIRST NAME"].toLowerCase()) {
        mismatches.push({ field: 'FIRST NAME', form: formData.firstName, api: apiData["FIRST NAME"] });
    }

    if (formData.lastName.toLowerCase() !== apiData["LAST NAME"].toLowerCase()) {
        mismatches.push({ field: 'LAST NAME', form: formData.lastName, api: apiData["LAST NAME"] });
    }

    // Normalize gender values before comparison
    const formGender = formData.gender.trim().toLowerCase();
    const apiGender = apiData.GENDER.replace(/[‘’]/g, '').trim().toLowerCase(); // Remove special quotes and trim

    if (formGender !== apiGender) {
        mismatches.push({ field: 'GENDER', form: formGender, api: apiGender });
    }

    // Convert form date of birth to DD/MM/YYYY format for comparison
    const [year, month, day] = formData.dob.split('-');
    const formattedFormDob = `${day}/${month}/${year}`;

    // Compare date of birth
    if (formattedFormDob !== apiData.DATE_OF_BIRTH) {
        mismatches.push({ field: 'DATE_OF_BIRTH', form: formattedFormDob, api: apiData.DATE_OF_BIRTH });
    }

    return mismatches;
}


app.post('/submit', upload.fields([{ name: 'front_image' }, { name: 'back_image' }]), async (req, res) => {
    const formData = new FormData();

    if (req.files.front_image && req.files.front_image.length > 0) {
        formData.append('front_image', fs.createReadStream(req.files.front_image[0].path));
    } else {
        console.log('No front_image uploaded');
    }

    if (req.files.back_image && req.files.back_image.length > 0) {
        formData.append('back_image', fs.createReadStream(req.files.back_image[0].path));
    } else {
        console.log('No back_image uploaded');
    }

    try {
        // Send the images to the external API for OCR
        const response = await axios.post('http://127.0.0.1:5000/upload', formData, {
            headers: {
                ...formData.getHeaders(), // Set correct headers for form-data
            },
        });

        const apiData = response.data;
        console.log('API response data:', apiData);

        // Extract the form data
        const formDataFromUser = {
            firstName: req.body.firstName,
            lastName: req.body.lastName,
            gender: req.body.gender,
            aadhar: req.body.aadhar,
            dob: req.body.dob,
        };

        // Compare form data with API data
        const mismatches = matchData(formDataFromUser, apiData);

        if (mismatches.length === 0) {
            // If no mismatches, insert data into MongoDB
            const usersCollection = client.db('test').collection('users'); // Change 'your_database_name' accordingly

            const newUser = {
                firstName: formDataFromUser.firstName,
                lastName: formDataFromUser.lastName,
                gender: formDataFromUser.gender,
                aadhar: formDataFromUser.aadhar,
                dob: formDataFromUser.dob,
                apiData: apiData // Optionally store API data
            };

            await usersCollection.insertOne(newUser); // Insert the new user data
            res.status(201).send('Data matches successfully and saved to database!');
        } else {
            // Return the mismatches if any
            res.status(200).json({
                message: 'Data mismatch found',
                mismatches: mismatches,
            });
        }
    } catch (error) {
        console.error('Error uploading images or matching data:', error);
        res.status(500).send('Error processing request');
    }
});

// Serve the HTML form
app.get('/upload', (req, res) => res.render('index'));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
