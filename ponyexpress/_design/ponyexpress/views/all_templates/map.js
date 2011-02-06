function(doc) {
	if(doc.doc_type == 'PonyExpressTemplate') {
		emit(doc._id, doc);
	}
}
