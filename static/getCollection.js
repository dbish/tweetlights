function loadCollection(){
	console.log('loading collection');
	var collection = document.getElementById('highlights');
	console.log(collection.getAttribute('collectionID'));
	twttr.widgets.createTimeline(
		{
			sourceType: "collection",
			id: collection.getAttribute('collectionID')
		},
		collection
	);
}
window.onload = function(){
	loadCollection();
};
