async function fetchData(url) {
    try {
      const response = await fetch(url);
  
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
  
      const data = await response.json(); 
      return data;
  
    } catch (error) {
      console.error('Fetch error:', error);
      return null; 
    }
  }
  
  // Example Usage:
  const apiUrl = 'https://s4crm.applexus.com:8888/sap/opu/odata/APLXCR/POS_MR_MAIN_SRV/MainSet?$format=json&$filter=IDateFrom%20eq%20%2720230108%27%20and%20IDateTo%20eq%20%2720250116%27'; 
  
  const fs = require('fs');
  const https = require('https');
  
  const ca = fs.readFileSync('sealinuxvm30.crt'); 
  
  const options = {
    ca: ca,
    rejectUnauthorized: false // Important: Keep this true for security
  };
  
  fetchData(apiUrl,options)
    .then(data => {
      if (data) {
        // Process the received data
        console.log(data); 
        // Example: Display data on the page
        const dataList = document.getElementById('data-list');
        data.forEach(item => {
          const listItem = document.createElement('li');
          listItem.textContent = item.name; // Replace with the relevant property
          dataList.appendChild(listItem);
        });
      }
    });