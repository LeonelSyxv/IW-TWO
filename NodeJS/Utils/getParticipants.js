const dbRequest = indexedDB.open('model-storage');

dbRequest.onsuccess = function(event) {
  const db = event.target.result;
  const tx = db.transaction(['participant'], 'readonly');
  const store = tx.objectStore('participant');
  const request = store.getAll();

  request.onsuccess = function() {
    const participants = request.result;
    const filtered = participants.filter(p =>
      typeof p.groupId === 'string' &&
      (p.groupId === "120363337403652171@g.us" || p.groupId === "5214921897369-1449534856@g.us")
    );
    console.log(filtered);
  };

  request.onerror = function() {
    console.error('Error reading participant');
  };
};