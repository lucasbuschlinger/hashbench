import hashlib

def main():



    with open("resources/hashes/top10k.txt", "r") as source:
        with open("resources/hashes/top10k.md5", "a") as _md5:
            with open("resources/hashes/top10k.md4", "a") as _md4:
                with open("resources/hashes/top10k.sha1", "a") as _sha1:
                    with open("resources/hashes/top10k.sha256", "a") as _sha256:
                        with open("resources/hashes/top10k.sha512", "a") as _sha512:

                            lines = source.readlines()
                            for line in lines:
                                md5_ = hashlib.md5()
                                sha1_ = hashlib.sha1()
                                sha256_ = hashlib.sha256()
                                sha512_ = hashlib.sha512()
                                b = bytes(line, 'utf-8')
                                md5_.update(b)
                                sha1_.update(b)
                                sha256_.update(b)
                                sha512_.update(b)
                                _md5.write(md5_.hexdigest()+'\n')
                                _sha1.write(sha1_.hexdigest()+'\n')
                                _sha256.write(sha256_.hexdigest()+'\n')
                                _sha512.write(sha512_.hexdigest()+'\n')
main()
