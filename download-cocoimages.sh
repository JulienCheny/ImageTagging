function downloadAndMoveInDocker() 
{
	if [ -f $1".zip" ]
	then
		echo "Zip file "$1" already exists"
	else
		echo "Download zip file "$1
		#wget "http://images.cocodataset.org/zips/"$1".zip"
	fi

	echo "dezip file"

	unzip $1".zip" -d app/

	echo "copy files to datas directory"

	docker-compose exec pycoco mv "app/"$1 "datas/images/"$1
}

downloadAndMoveInDocker train2014
#downloadAndMoveInDocker train2017
downloadAndMoveInDocker val2014
#downloadAndMoveInDocker val2017
