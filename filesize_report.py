from reports import *

def filesize_report(args):


    Folders = StanzaFactory(args,
                            """Select distinct source AS SourceID
                               From RELATIONS r
                               Where r.type='AccessRelationship' and r.Name='Establish'"""
                            )
    Folders.add_report_segment(
        SegmentSQL("""SELECT ID, Type, Name, Documentation
                    FROM elements
                    Where ID='{SourceID}'""")
    )


    Elements = StanzaFactory(args,
                             """Select Distinct r2.Source as ArtID
                                From RELATIONS r
                                INNER JOIN relations r2 on r2.Target=r.Target and r.Source='{SourceID}'
                                Where r.type='AccessRelationship' and r.Name='Establish'
                                and r2.type='RealizationRelationship' and (r2.Name='Uncompressed' or r2.Name='Lossy' or r2.name='Lossless')"""
                             )
    Elements.add_report_segment(
        SegmentSQL("""with propertypivot(source, NumOfFiles, FileSize, Frequency, Down, Reuse, Debug) as (Select r.source,
CASE Key when 'Req:NumOfFiles' then Value ELSE NULL End as NumOfFiles,
CASE Key when 'Req:Filesize' then Value ELSE NULL End as FileSize,
CASE Key when 'Req:Frequency' then Value ELSE NULL End as Frequency,
CASE Key when 'Time:Down' then Value ELSE NULL End as Down,
CASE Key when 'Time:Reuse' then Value ELSE NULL End as Reuse,
CASE Key when 'Time:Debug' then Value ELSE NULL End as Debug
From RELATIONS r
INNER JOIN properties p on r.source=p.id
Where r.type='RealizationRelationship' and (r.Name='Uncompressed' or r.Name='Lossy' or r.name='Lossless') and r.Source='{ArtID}')
select r.Source, r.Type, r.Name, /* pNum.NumOfFIles, pSize.FileSize, pFreq.Frequency, tDown.Down, tReuse.Reuse, tDebug.Debug,*/
CASE
        WHEN CAST(tDown.Down AS INT) >= CAST(tReuse.Reuse AS INT) AND CAST(tDown.Down AS INT) >= CAST(tDebug.Debug AS INT) THEN (CAST(tDown.Down AS INT)/CAST(pFreq.Frequency AS INT))*CAST(pNum.NumOfFIles AS INT)*CAST(pSize.FileSize AS INT)
        WHEN CAST(tReuse.Reuse AS INT) >= CAST(tDown.Down AS INT) AND CAST(tReuse.Reuse AS INT) >= CAST(tDebug.Debug AS INT) THEN (CAST(tReuse.Reuse AS INT)/CAST(pFreq.Frequency AS INT))*CAST(pNum.NumOfFIles AS INT)*CAST(pSize.FileSize AS INT)
        WHEN CAST(tDebug.Debug AS INT) >= CAST(tDown.Down AS INT) AND CAST(tDebug.Debug AS INT) >= CAST(tReuse.Reuse AS INT) THEN (CAST(tDebug.Debug AS INT)/CAST(pFreq.Frequency AS INT))*CAST(pNum.NumOfFIles AS INT)*CAST(pSize.FileSize AS INT)
        ELSE (CAST(tDown.Down AS INT)/CAST(pFreq.Frequency AS INT))*CAST(pNum.NumOfFIles AS INT)*CAST(pSize.FileSize AS INT)
    END AS BytesNeeded
From RELATIONS r
INNER JOIN propertypivot pNum on pNum.source=r.source AND pNum.NumOfFIles IS NOT NULL
INNER JOIN propertypivot pSize on pSize.source=r.source AND pSize.FileSize IS NOT NULL
INNER JOIN propertypivot pFreq on pFreq.source=r.source AND pFreq.Frequency IS NOT NULL
INNER JOIN propertypivot tDown on tDown.source=r.source AND tDown.Down IS NOT NULL
INNER JOIN propertypivot tReuse on tReuse.source=r.source AND tReuse.Reuse IS NOT NULL
INNER JOIN propertypivot tDebug on tDebug.source=r.source AND tDebug.Debug IS NOT NULL
Where r.type='RealizationRelationship' and (r.Name='Uncompressed' or r.Name='Lossy' or r.name='Lossless')""")
    )

    Folders.set_substanza(Elements)


    # Folders.report({})
    return Folders
