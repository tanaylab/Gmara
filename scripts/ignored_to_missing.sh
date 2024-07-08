
for IGNORED in genes/*/namespaces/sources/*.Ignored.txt
do
    MISSING=`echo $IGNORED | sed 's/Ignored/Missing/'`
    if [ -f $IGNORED ]
    then
        cat $IGNORED >> $MISSING
        rm $IGNORED
    fi
done
