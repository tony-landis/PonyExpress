function(doc) {
	if(doc.doc_type=='PonyExpressMessage' && (doc.status=='queued' || doc.status=='failed')) {
		emit([doc.status, 1);
	}
}

