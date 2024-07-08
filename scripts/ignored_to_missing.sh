
for IGNORED in genes/*/namespaces/sources/*.Ignored.tsv
do
    MISSING=`echo $IGNORED | sed 's/Ignored/Missing/'`
    if [ -f $IGNORED ]
    then
        cat $IGNORED >> $MISSING
        rm $IGNORED
    fi
done
