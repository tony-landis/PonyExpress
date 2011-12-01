function(doc) {
	if(doc.doc_type=='PonyExpressMessage' && doc.date == null) {
		emit(doc._id, null);
	}
}
