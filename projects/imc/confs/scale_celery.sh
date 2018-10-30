
if [ $# -eq 0 ];
then
	echo "Missing argument: number of instances"
	exit 1
fi

rapydo --mode workers scale celery=0
rapydo --mode workers scale celery=$1

for i in `seq 1 $1`
do
	echo "Applying patch to celery_worker$i..."

	docker exec --user root \
	            -it imc_celery_$i \
	            sed -i -e "s/\${HOSTNAME}/celery_worker${i}/g" /usr/local/bin/mycelery

	docker restart imc_celery_$i
done

echo "Refreshing flower known instances"
docker restart imc_celeryui_1