from pathlib import Path
p=Path('backend/app/models.py');s=p.read_text();s=s.replace('    DateTime,','    DateTime,\n    Date,');s=s.replace('    email = Column(String(255)', '    rut = Column(String(12), unique=True, nullable=True)\n    telefono = Column(String(30), nullable=True)\n    fecha_identidad = Column(Date, nullable=True)\n    email = Column(String(255)',1);s=s.replace('    logo_url = Column(String(255))','    logo_url = Column(String(255))\n    foto_id = Column(String(32), ForeignKey("archivos_portfolio.id"), nullable=True)');p.write_text(s)
p=Path('backend/app/schemas.py');s=p.read_text().replace('from datetime import datetime','from datetime import datetime, date');s=s.replace('info.field_name != "password"','info.field_name not in ("password", "password_actual")');s=s.replace('class RegistroEgresado(InputModel):','''class RegistroIdentidad(InputModel):
    rut: str = Field(min_length=3, max_length=12)
    telefono: str = Field(min_length=8, max_length=30)
    fecha_identidad: date

    @field_validator('rut')
    @classmethod
    def valid_rut(cls, value):
        import re
        raw = value.replace('.', '').replace('-', '').upper()
        if not re.fullmatch(r'[1-9][0-9]{6,7}[0-9K]', raw):
            raise ValueError('Ingresa un RUT chileno válido.')
        body, digit = raw[:-1], raw[-1]
        total = sum(int(n) * (2 + i % 6) for i, n in enumerate(reversed(body)))
        expected = '0123456789K0'[11 - total % 11]
        if digit != expected:
            raise ValueError('El dígito verificador del RUT no es válido.')
        return body + '-' + digit

    @field_validator('telefono')
    @classmethod
    def valid_phone(cls, value):
        import re
        value = re.sub(r'[ ()-]', '', value)
        if not re.fullmatch(r'\\+?[0-9]{8,15}', value):
            raise ValueError('Ingresa un teléfono válido, con código de país si corresponde.')
        return value

    @field_validator('fecha_identidad')
    @classmethod
    def valid_date(cls, value):
        if value > date.today():
            raise ValueError('La fecha no puede estar en el futuro.')
        return value


class RegistroEgresado(RegistroIdentidad):''');s=s.replace('    carrera: Optional[Annotated[str, Field(max_length=150)]] = None','    carrera: Annotated[str, Field(min_length=1, max_length=150)]',1);s=s.replace('class RegistroEmpresa(InputModel):','class RegistroEmpresa(RegistroIdentidad):');s=s.replace('    rubro: Optional[Annotated[str, Field(max_length=150)]] = None','    rubro: Annotated[str, Field(min_length=1, max_length=150)]',1)
s=s.replace('class PerfilEmpresaOut(BaseModel):','''class PerfilEmpresaUpdate(InputModel):
    nombre_empresa: Annotated[str, Field(min_length=1, max_length=150)]
    descripcion: str = Field(max_length=5000)
    foto_id: Optional[Annotated[str, Field(pattern=r'^[a-f0-9]{32}$')]] = None


class CambioPassword(InputModel):
    password_actual: str = Field(min_length=1, max_length=72)
    password: str = Field(min_length=8, max_length=72)


class PerfilEmpresaOut(BaseModel):''');s=s.replace('    logo_url: Optional[str] = None','    logo_url: Optional[str] = None\n    foto_id: Optional[str] = None');p.write_text(s)
p=Path('backend/app/routers/auth.py');s=p.read_text();s=s.replace('    user = models.Usuario(email=email, password_hash=hash_password(data.password), tipo=role)','''    if db.query(models.Usuario).filter_by(rut=data.rut).first():
        raise HTTPException(409, "Ese RUT ya está registrado.")
    user = models.Usuario(email=email, password_hash=hash_password(data.password), tipo=role,
                          rut=data.rut, telefono=data.telefono, fecha_identidad=data.fecha_identidad)''');s=s.replace('{"email", "password"}', '{"email", "password", "rut", "telefono", "fecha_identidad"}');s=s.replace('Verifica si el correo ya está registrado.', 'Verifica si el correo o RUT ya están registrados.');s+='''

@router.post('/password', response_model=schemas.SessionOut, dependencies=[Depends(limit_auth)])
def change_password(data: schemas.CambioPassword, user=Depends(current_user), db: Session=Depends(get_db)):
    # Serialize concurrent password changes and invalidate every previous JWT.
    user = db.query(models.Usuario).filter_by(id=user.id).populate_existing().with_for_update().one()
    if not verify_password(data.password_actual, user.password_hash):
        raise HTTPException(400, 'La contraseña actual no es correcta.')
    if data.password_actual == data.password:
        raise HTTPException(422, 'Elige una contraseña distinta de la actual.')
    user.password_hash = hash_password(data.password)
    user.token_version += 1
    db.commit()
    return {'access_token': create_token(user.id, user.token_version), 'user': user}
''';p.write_text(s)
p=Path('backend/app/routers/empresas.py');s=p.read_text();s+='''

@router.put('/{usuario_id}/perfil', response_model=schemas.PerfilEmpresaOut)
def update_company_profile(usuario_id: int, data: schemas.PerfilEmpresaUpdate, db: Session=Depends(get_db)):
    profile = _obtener_perfil_empresa_o_404(db, usuario_id)
    if data.foto_id:
        asset = db.get(models.ArchivoPortfolio, data.foto_id)
        if not asset or asset.usuario_id != usuario_id or asset.tipo != 'foto' or not asset.verificado:
            raise HTTPException(422, 'Selecciona una foto verificada de tu propia cuenta.')
    for key, value in data.model_dump().items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile
''';p.write_text(s)
