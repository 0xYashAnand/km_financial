import React, { useState } from "react";
import {
  TextField,
  Button,
  Grid,
  Typography,
  Container,
  MenuItem,
} from "@mui/material";
import api from "../../api";
import { useHistory} from "react-router-dom";
import axios from 'axios';


const LoanForm = () => {
  const history = useHistory();
  const [formData, setFormData] = useState({
    "applicant_name": "Yash Anand",
    "aadhar_no": "250825082508",
    "pan_no": "DDKLT5840M",
    "bank_details": "Bank Of India, Branch Name",
    "account_no": "1234567890",
    "ifsc_code": "BKID0002541",
    "loan_amount": 10000.0,
    "loan_type": "Other Loans",
    "annual_interest_rate": 5.0, // Example value, adjust as necessary
    "loan_term": 12, // Example value, adjust as necessary
    "employment_details":"Others"// Example value, adjust as necessary
    
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const accessToken = localStorage.getItem("accessToken"); 
      
      const headers = {
        "token": `${accessToken}`,
        "Content-Type": "application/json",
       };
        
      const response = await axios.post(
       
        "http://localhost:8000/apply-loan",
        formData,
        {headers},
      );
      alert(response.data.message); 
      history.push("/");
    } catch (error) {
      alert("Error submitting loan application:", error.response.data.detail);
    }
  };

  
  const loanTypes = [
    "Buissness Loans",
    "Personal Loans",
    "Home Loans",
    "Vehicle Loans",
    "Education Loans",
    "Other Loans",
  ];

  const employmentTypes = [
    "Salaried",
    "Non-Salaried",
    "Unemployed",
    "Student",
    "Others",
  ];

  return (
    <Container maxWidth="md">
      <form onSubmit={handleSubmit}>
        <Grid
          container
          spacing={4}
          sx={{ padding: "20px", margin: "20px", backgroundColor: "#f0f0f0" }}
        >
          <Grid item xs={12}>
            <Typography variant="h5">Loan Application Form</Typography>
          </Grid>
          <Grid item xs={12}>
            <TextField
              type="text"
              id="applicant_name"
              name="applicant_name"
              label="Applicant Name"
              value={formData.applicant_name}
              onChange={handleChange}
              fullWidth
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              type="number"
              id="loan_amount"
              name="loan_amount"
              label="Loan Amount"
              value={formData.loan_amount}
              onChange={handleChange}
              fullWidth
              placeholder="Rs. 10000"
              InputProps={{
                inputMode: "numeric",
                pattern: "[0-9]*",
                maxLength: 8, // Maximum length of the number input
              }}
              inputProps={{
                min: 1000, // Minimum value
                max: 99999999, // Maximum value
              }}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              select
              id="loan_type"
              name="loan_type"
              label="Loan Type"
              value={formData.loan_type}
              onChange={handleChange}
              fullWidth
            >
              {loanTypes.map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </TextField>
          </Grid>

          <Grid item xs={12}>
            <TextField
              select
              id="employment_details"
              name="employment_details"
              label="Employment Details"
              value={formData.employment_details}
              onChange={handleChange}
              fullWidth
            >
              {employmentTypes.map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </TextField>
          </Grid>

          <Grid item xs={12}>
            <TextField
              type="text"
              id="aadhar_no"
              name="aadhar_no"
              label="Aadhar Number"
              value={formData.aadhar_no}
              onChange={handleChange}
              fullWidth
              inputProps={{ maxLength: 12 }}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              type="text"
              id="pan_no"
              name="pan_no"
              label="PAN Number"
              value={formData.pan_no}
              onChange={handleChange}
              fullWidth
              inputProps={{ maxLength: 10 }}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              type="text"
              id="bank_name"
              name="bank_name"
              label="Bank Name"
              value={formData.bank_details}
              onChange={handleChange}
              fullWidth
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              type="text"
              id="account_no"
              name="account_no"
              label="Account Number"
              value={formData.account_no}
              onChange={handleChange}
              fullWidth
              inputProps={{ maxLength: 15 }}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              type="text"
              id="bank_ifsc"
              name="bank_ifsc"
              label="IFSC Code"
              value={formData.ifsc_code}
              onChange={handleChange}
              fullWidth
              inputProps={{ maxLength: 10 }}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              type="text"
              id="annual_interest_rate"
              name="annual_interest_rate"
              label="Annual Intrest rate"
              value={formData.annual_interest_rate}
              onChange={handleChange}
              fullWidth
              inputProps={{ maxLength: 10 }}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              type="text"
              id="loan_term"
              name="loan_term"
              label="Loan Term"
              value={formData.annual_interest_rate}
              onChange={handleChange}
              fullWidth
              inputProps={{ maxLength: 10 }}
            />
          </Grid>

          <Grid item xs={12}>
            <Button type="submit" variant="contained" color="primary">
              Apply Loan
            </Button>
          </Grid>
        </Grid>
      </form>
    </Container>
  );
};

export default LoanForm;