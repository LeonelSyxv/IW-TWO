const dbRequest = indexedDB.open('model-storage');

dbRequest.onsuccess = function(event) {
  const db = event.target.result;
  const tx = db.transaction(['group-metadata'], 'readonly');
  const store = tx.objectStore('group-metadata');
  const request = store.getAll();

  request.onsuccess = function() {
    const groups = request.result;
    const filtered = groups.filter(g =>
      typeof g.subject === 'string' &&
      (g.subject === 'Monitoreo StarTV Stream' || g.subject === 'Monitoreo')
    );
    console.log(filtered);
  };

  request.onerror = function() {
    console.error('Error reading group-metadata');
  };
};