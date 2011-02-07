function(doc) {
	if(doc.doc_type == 'PonyExpressMessage') {
		emit(doc.status, doc);
	}
}
