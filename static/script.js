// SCRIPT.JS
var socket = io();

// LISTEN FOR 'UPDATE_DATA' EVENT FROM THE SERVER
socket.on('update_data', function (data) {
  const tableBody = document.getElementById('crypto-table-body');
  tableBody.innerHTML = ''; // CLEAR EXISTING TABLE CONTENT

  // ITERATE OVER THE RECEIVED DATA AND POPULATE THE TABLE
  data.forEach(
    ([
      name,
      price,
      change,
      change_percent,
      logo_url,
      market_cap,
      circulating_supply,
    ]) => {
      const row = document.createElement('tr');

      // PARSE NUMERIC VALUES AND DETERMINE COLORS FOR CHANGE INDICATORS
      const changeValue = parseFloat(change.replace(/[^0-9.-]+/g, ''));
      const changePercentValue = parseFloat(
        change_percent.replace(/[^0-9.-]+/g, '')
      );

      const changeColor =
        changeValue > 0 ? 'green' : changeValue < 0 ? 'red' : '';
      const changePercentColor =
        changePercentValue > 0 ? 'green' : changePercentValue < 0 ? 'red' : '';

      // BUILD THE TABLE ROW WITH DATA
      row.innerHTML = `
          <td><img src="${logo_url}" alt="${name} logo" class="crypto-logo"><span class="crypto-name">${name}</span></td>
          <td>${price}</td>
          <td style="color: ${changeColor}">${change}</td>
          <td style="color: ${changePercentColor}">${change_percent}</td>
          <td>${market_cap}</td>
          <td>${circulating_supply}</td>
      `;
      tableBody.appendChild(row); // ADD THE ROW TO THE TABLE BODY
    }
  );
});
