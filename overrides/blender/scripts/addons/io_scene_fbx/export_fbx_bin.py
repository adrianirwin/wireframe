# export_fbx_bin.py -> Write VertexColor Layers. [modified 18.03.2015 by ByteRockers' Games] see: http://forum.unity3d.com/threads/vertex-rgba-blender-2-5x.254038/

    # vcolnumber = len(me.vertex_colors)
    vcolnumber = 0
    for collayer in me.vertex_colors: # NEW
        if collayer.name.endswith('_ALPHA'): # NEW
                continue # NEW
        vcolnumber += 1 # NEW

    if vcolnumber:
        # def _coltuples_gen(raw_cols):
        def _coltuples_gen(raw_cols, in_alpha_cols): # NEW
            # return zip(*(iter(raw_cols),) * 3 + (_infinite_gen(1.0),))  # We need a fake alpha...
            return zip(*(iter(raw_cols),) * 3 + (iter(in_alpha_cols),) * 1) # NEW

        t_lc = array.array(data_types.ARRAY_FLOAT64, (0.0,)) * len(me.loops) * 3
        colindex = -1 # NEW

        for colindex, collayer in enumerate(me.vertex_colors):

            if collayer.name.endswith('_ALPHA'): # NEW
                continue # NEW

            alphalayer_alpha = [1.0] * len(collayer.data) # NEW
            if collayer.name+'_ALPHA' in me.vertex_colors.keys(): # NEW
                collayer_alpha = me.vertex_colors[collayer.name+'_ALPHA'] # NEW
                for idx,colordata in enumerate(collayer_alpha.data): # NEW
                    alphaValue = ( (colordata.color.r + colordata.color.g + colordata.color.b) / 3.0) # NEW
                    alphalayer_alpha[idx] = alphaValue # NEW

            collayer.data.foreach_get("color", t_lc)
            lay_vcol = elem_data_single_int32(geom, b"LayerElementColor", colindex)
            elem_data_single_int32(lay_vcol, b"Version", FBX_GEOMETRY_VCOLOR_VERSION)
            elem_data_single_string_unicode(lay_vcol, b"Name", collayer.name)
            elem_data_single_string(lay_vcol, b"MappingInformationType", b"ByPolygonVertex")
            elem_data_single_string(lay_vcol, b"ReferenceInformationType", b"IndexToDirect")

            # col2idx = tuple(set(_coltuples_gen(t_lc)))
            col2idx = tuple(set(_coltuples_gen(t_lc,alphalayer_alpha))) # NEW
            elem_data_single_float64_array(lay_vcol, b"Colors", chain(*col2idx))  # Flatten again...

            col2idx = {col: idx for idx, col in enumerate(col2idx)}
            # elem_data_single_int32_array(lay_vcol, b"ColorIndex", (col2idx[c] for c in _coltuples_gen(t_lc)))
            elem_data_single_int32_array(lay_vcol, b"ColorIndex", (col2idx[c] for c in _coltuples_gen(t_lc,alphalayer_alpha))) # NEW
            del col2idx
        del t_lc
        del _coltuples_gen
        # end of modification