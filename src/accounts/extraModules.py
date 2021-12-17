def prepareKeys(public, private):
    """
        Returns list of [n. e] as public key and [n, d] as private key from format 'n-e'
    """
    public = public.split('-')
    public = [int(key)/5 for key in public] # [n, e]
    private = private.split('-')
    private = [int(key)/5 for key in private] #[n, d]
    return public, private