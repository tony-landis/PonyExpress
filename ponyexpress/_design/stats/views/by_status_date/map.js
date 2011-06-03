function(doc) {
	if(doc.doc_type=='PonyExpressMessage') {
		ymd = doc.date.split('T');
		d = ymd[0].split("-");
		emit([doc.status, d[0], d[1], d[2]], 1);
	}
}

