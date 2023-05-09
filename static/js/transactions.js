const table = document.getElementById('transaction-tbody');

// Realiza el fetch a la URL '/getTransactions'
fetch('/getHistory')
  .then(response => response.json())
  .then(data => {
    const table = document.querySelector('.transactions-table');
    for (const [index, transaction] of Object.entries(data.transactions)) {
      const { FROM, TO, AMOUNT, TIME } = transaction;
      const row = table.insertRow(-1);
      row.insertCell(0).textContent = parseInt(index) + 1;
      
      [FROM, TO, AMOUNT, TIME].forEach((field, index) => {
        row.insertCell(index + 1).textContent = field;
      });
    }
  })